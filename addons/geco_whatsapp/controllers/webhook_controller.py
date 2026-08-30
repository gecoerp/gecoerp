# -*- coding: utf-8 -*-
import json
import logging
from datetime import datetime, timedelta

from odoo import fields, http
from odoo.http import request

_logger = logging.getLogger(__name__)


class GecoWhatsappWebhookController(http.Controller):

    @http.route('/geco_whatsapp/webhook/<string:account_ref>', type='http', auth='public',
                methods=['POST'], csrf=False, save_session=False)
    def whatsapp_webhook(self, account_ref, **kwargs):
        env = request.env
        response = self._handle(env, account_ref)
        return request.make_json_response(response[0], status=response[1])

    def _handle(self, env, account_ref):
        try:
            payload = json.loads(request.httprequest.data or b'{}')
        except (TypeError, ValueError):
            return {'error': 'invalid JSON body'}, 400

        log = env['geco.whatsapp.log'].sudo()

        account = env['geco.whatsapp.account'].sudo().search(
            [('external_account_id', '=', account_ref)], limit=1,
        )
        if not account:
            _logger.warning("Webhook recibido para cuenta desconocida: %s", account_ref)
            log.log_event('webhook_error', success=False,
                           detail="Webhook recibido para cuenta desconocida: %s" % account_ref)
            return {'error': 'unknown account'}, 404

        secret_header = request.httprequest.headers.get('X-Webhook-Secret')
        if not account.webhook_secret or secret_header != account.webhook_secret:
            _logger.warning("Webhook rechazado para cuenta %s: secreto inválido", account_ref)
            log.log_event('webhook_error', account=account, success=False,
                           detail="Secreto de webhook inválido")
            return {'error': 'invalid secret'}, 401

        event = payload.get('event')
        if event == 'status':
            self._handle_status_event(env, account, payload)
        elif event == 'message':
            self._handle_message_event(env, account, payload)
        else:
            return {'success': True, 'ignored': event}, 200

        return {'success': True}, 200

    def _handle_status_event(self, env, account, payload):
        vals = {}
        if payload.get('status'):
            vals['status'] = payload['status']
        if payload.get('phone'):
            vals['phone'] = payload['phone']
        if vals:
            account.write(vals)
        env['geco.whatsapp.log'].sudo().log_event(
            'status', account=account, phone=payload.get('phone'),
            detail="Estado actualizado a: %s" % payload.get('status'),
            raw_payload=json.dumps(payload, ensure_ascii=False, indent=2),
        )

    def _handle_message_event(self, env, account, payload):
        if payload.get('is_group') or (payload.get('from') or '').endswith('@g.us'):
            # Mensajes de grupo: fuera de alcance por ahora.
            return
        # 'phone' viene resuelto por el microservicio vía getContact(), no del JID
        # crudo (que puede venir como "@lid" y no ser el número real).
        phone = payload.get('phone') or (payload.get('from') or '').split('@')[0]
        if not phone:
            return
        content_type = payload.get('content_type') or 'text'
        raw_payload = json.dumps(payload, ensure_ascii=False, indent=2)

        if env['geco.whatsapp.ignore'].sudo().is_ignored(phone, company=account.company_id):
            env['geco.whatsapp.log'].sudo().log_event(
                'inbound', account=account, phone=phone, content_type=content_type, success=True,
                detail="Mensaje ignorado (número en la lista de ignorados).", raw_payload=raw_payload,
            )
            return

        partner = env['geco.whatsapp.service'].sudo().find_or_create_partner(
            phone, name=payload.get('sender_name'), image_base64=payload.get('sender_avatar_base64'),
            account=account,
        )
        # Sin esto, Odoo nunca avisa nada: message_post solo notifica a quien ya
        # sigue el registro. Se suscribe al responsable para que le llegue al
        # icono de mensajes (bandeja), igual que ya le llegan los de Discuss.
        self._ensure_follower(env, partner, self._resolve_responsible_user(env, partner))

        attachment_ids = []
        media = payload.get('media') or {}
        if payload.get('has_media') and media.get('data'):
            attachment = env['ir.attachment'].sudo().create({
                'name': media.get('filename') or 'archivo',
                'datas': media['data'],
                'mimetype': media.get('mimetype') or 'application/octet-stream',
            })
            attachment_ids = [attachment.id]

        reply_text = None

        # Para ubicación y contacto, WhatsApp mete datos crudos en "body" (el
        # base64 de la miniatura del mapa, o el vCard completo) — no es texto
        # para mostrar. Se descarta y solo se usa el resumen limpio de abajo.
        body = '' if content_type in ('location', 'contact') else (payload.get('body') or '')
        location = payload.get('location')
        if location and location.get('latitude') and location.get('longitude'):
            lat, lng = location['latitude'], location['longitude']
            partner.sudo().write({'partner_latitude': lat, 'partner_longitude': lng})
            maps_url = "https://maps.google.com/?q=%s,%s" % (lat, lng)
            location_line = "📍 Compartió su ubicación: %s" % maps_url
            body = "%s\n%s" % (body, location_line) if body else location_line
            reply_text = "📍 Ubicación recibida y registrada."

        service = env['geco.whatsapp.service'].sudo()
        contact_lines = []
        for shared in (payload.get('contacts') or []):
            shared_phone = shared.get('phone')
            if not shared_phone:
                continue
            shared_name = shared.get('name')
            existing = service.find_partner_by_phone(
                service.normalize_phone(shared_phone, account=account), company=account.company_id,
            )
            if not existing:
                action_label = "contacto nuevo creado"
            elif shared_name and existing.name != shared_name:
                action_label = "nombre actualizado"
            else:
                action_label = "ya existía, sin cambios"
            shared_partner = service.find_or_create_partner(
                shared_phone, name=shared_name, update_if_exists=True, account=account,
            )
            contact_lines.append("👤 %s (%s): %s" % (shared_name or shared_phone, shared_phone, action_label))
            env['geco.whatsapp.log'].sudo().log_event(
                'inbound', account=account, phone=shared_phone, partner_id=shared_partner.id,
                content_type='contact', detail="Contacto compartido — %s" % action_label,
            )
        if contact_lines:
            contacts_block = "\n".join(contact_lines)
            body = "%s\n%s" % (body, contacts_block) if body else contacts_block
            reply_text = (
                "👤 Contacto recibido y registrado." if len(contact_lines) == 1
                else "👤 Contactos recibidos y registrados."
            )

        failed_vcards = payload.get('contacts_failed_raw')
        if failed_vcards and not contact_lines:
            # El vCard llegó pero no se pudo extraer un teléfono (p.ej. el contacto
            # compartido también usa la privacidad "@lid" de WhatsApp) — antes esto
            # se perdía en silencio; ahora queda visible en el chatter y la bitácora.
            fail_line = "⚠️ Se recibió un contacto compartido, pero no se pudo leer su teléfono."
            body = "%s\n%s" % (body, fail_line) if body else fail_line
            env['geco.whatsapp.log'].sudo().log_event(
                'inbound', account=account, phone=phone, partner_id=partner.id,
                content_type='contact', success=False,
                detail="No se pudo extraer teléfono del vCard: %s" % failed_vcards[0],
            )

        if payload.get('is_event'):
            event_info = payload.get('event_info') or {}
            event_name = event_info.get('name') or 'Evento sin título'
            start, stop, is_placeholder_date = self._resolve_event_datetimes(event_info)
            responsible_id = self._resolve_responsible_user(env, partner)
            conflicts = self._find_calendar_conflicts(env, responsible_id, start, stop)

            event_line = "📅 Compartió un evento de WhatsApp: %s — %s" % (
                event_name, fields.Datetime.to_string(start),
            )
            if conflicts:
                event_line += "\n⚠️ Choca en horario con: %s" % ", ".join(conflicts.mapped('name'))
            body = "%s\n%s" % (body, event_line) if body else event_line

            self._create_event_activity(env, partner, event_info, start, conflicts)
            self._create_event_meeting(
                env, partner, event_info, start, stop, is_placeholder_date, responsible_id, conflicts,
            )

            if conflicts:
                reply_text = (
                    "📅 Evento recibido y registrado: %s — ⚠️ OJO, ya tienes algo agendado en ese "
                    "horario (%s). Revisa el Calendario." % (event_name, ", ".join(conflicts.mapped('name')))
                )
            else:
                reply_text = "📅 Evento recibido y registrado: %s" % event_name

        partner.message_post(
            body=body,
            attachment_ids=attachment_ids,
            message_type='comment',
            subtype_xmlid='mail.mt_comment',
            author_id=partner.id,
            whatsapp_inbound=True,
        )
        env['geco.whatsapp.log'].sudo().log_event(
            'inbound', account=account, phone=phone, partner_id=partner.id,
            content_type=content_type, detail=(payload.get('body') or '')[:200],
            raw_payload=raw_payload,
        )

        if reply_text:
            partner.message_post(
                body=reply_text, message_type='comment',
                whatsapp_send=True, whatsapp_phone=phone,
            )

    def _ensure_follower(self, env, partner, user_id):
        user = env['res.users'].sudo().browse(user_id)
        if user.partner_id and user.partner_id not in partner.message_partner_ids:
            partner.sudo().message_subscribe(partner_ids=[user.partner_id.id])

    def _resolve_responsible_user(self, env, partner):
        """Cascada: Vendedor del contacto → Comprador → responsable del Equipo
        de ventas → usuario de sistema, como respaldo final."""
        if partner.user_id:
            return partner.user_id.id
        if partner.buyer_id:
            return partner.buyer_id.id
        if partner.team_id and partner.team_id.user_id:
            return partner.team_id.user_id.id
        admin = env.ref('base.user_admin', raise_if_not_found=False)
        return admin.id if admin else env.user.id

    def _resolve_event_datetimes(self, event_info):
        """Devuelve (start, stop, is_placeholder). Si WhatsApp trajo la fecha/hora
        real del evento se usa tal cual; si no, se cae al mismo respaldo de
        antes (marcador temporal de 1 hora desde ahora)."""
        if event_info.get('start_timestamp'):
            start = datetime.utcfromtimestamp(event_info['start_timestamp'])
            stop = (
                datetime.utcfromtimestamp(event_info['end_timestamp'])
                if event_info.get('end_timestamp') else start + timedelta(hours=1)
            )
            return start, stop, False
        start = fields.Datetime.now()
        return start, start + timedelta(hours=1), True

    def _find_calendar_conflicts(self, env, user_id, start, stop):
        """Reuniones ya agendadas para el mismo responsable que se traslapan
        con [start, stop). Solo cuentan las marcadas 'Ocupado' (show_as=busy)."""
        return env['calendar.event'].sudo().search([
            ('user_id', '=', user_id),
            ('show_as', '=', 'busy'),
            ('start', '<', stop),
            ('stop', '>', start),
        ])

    def _create_event_activity(self, env, partner, event_info, start, conflicts):
        event_info = event_info or {}
        name = event_info.get('name') or 'evento de WhatsApp'
        note_lines = ['%s compartió el evento "%s" por WhatsApp.' % (partner.name, name)]
        if event_info.get('description'):
            note_lines.append("Descripción: %s" % event_info['description'])
        note_lines.append("Fecha: %s" % fields.Datetime.to_string(start))
        if event_info.get('location_name'):
            note_lines.append("Lugar: %s" % event_info['location_name'])
        if event_info.get('join_link'):
            note_lines.append("Link: %s" % event_info['join_link'])
        if conflicts:
            note_lines.append("⚠️ Choca en horario con: %s" % ", ".join(conflicts.mapped('name')))
        note_lines.append("Ya se creó la reunión correspondiente en el Calendario.")
        partner.sudo().activity_schedule(
            act_type_xmlid='mail.mail_activity_data_todo',
            summary="Revisar evento de WhatsApp: %s" % name,
            note="<br/>".join(note_lines),
            date_deadline=start.date(),
            user_id=self._resolve_responsible_user(env, partner),
        )

    def _create_event_meeting(self, env, partner, event_info, start, stop, is_placeholder_date,
                               responsible_id, conflicts):
        event_info = event_info or {}
        title = event_info.get('name') or ("Evento de WhatsApp — %s" % partner.name)
        if is_placeholder_date:
            title = "⚠️ Evento de WhatsApp sin confirmar — %s" % partner.name
        if conflicts:
            title = "⚠️ CONFLICTO — %s" % title

        description_parts = ["%s compartió este evento por WhatsApp." % partner.name]
        if event_info.get('description'):
            description_parts.append(event_info['description'])
        if is_placeholder_date:
            description_parts.append(
                "No se pudo leer la fecha/hora real — este es un marcador temporal, "
                "ábrelo en WhatsApp para confirmar y corrígela."
            )
        if conflicts:
            description_parts.append(
                "⚠️ Choca en horario con: %s — revisa cuál se queda." % ", ".join(conflicts.mapped('name'))
            )

        vals = {
            'name': title,
            'start': start,
            'stop': stop,
            'user_id': responsible_id,
            'partner_ids': [(4, partner.id)],
            'description': "<br/>".join(description_parts),
        }
        if event_info.get('location_name'):
            vals['location'] = event_info['location_name']
        if event_info.get('join_link'):
            vals['videocall_location'] = event_info['join_link']
        return env['calendar.event'].sudo().create(vals)
