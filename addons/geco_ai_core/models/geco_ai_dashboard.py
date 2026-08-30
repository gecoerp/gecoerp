# -*- coding: utf-8 -*-
from odoo import models, api
import datetime
import pandas as pd
import numpy as np
from sklearn.neural_network import MLPRegressor
from collections import defaultdict

class GecoAiDashboard(models.AbstractModel):
    _name = 'geco.ai.dashboard'
    _description = 'GECO AI Dashboard Backend'

    @api.model
    def get_statistics(self):
        today = datetime.date.today()
        first_day = today.replace(day=1)
        next_month = (first_day + datetime.timedelta(days=32)).replace(day=1)
        days_in_month = (next_month - first_day).days
        days_passed = today.day

        # Get all logs for ML training
        all_logs = self.env['geco.ai.log'].search([])
        
        # 1. KPIs - Current Month
        logs_this_month = all_logs.filtered(lambda l: l.create_date.date() >= first_day)
        total_tokens_month = sum(logs_this_month.mapped('tokens_total'))
        total_cost_month = sum(logs_this_month.mapped('cost_estimate'))

        token_limit = int(self.env['ir.config_parameter'].sudo().get_param('geco_ai.token_limit', 0))

        # Rolling 30 days for Average Daily (so it's not 0 at start of month)
        thirty_days_ago = today - datetime.timedelta(days=29)
        logs_30_days = all_logs.filtered(lambda l: l.create_date.date() >= thirty_days_ago)
        total_30_days = sum(logs_30_days.mapped('tokens_total'))
        average_daily = round(total_30_days / 30.0)

        # -------------------------------------------------------------
        # MACHINE LEARNING PROJECTIONS (Pandas + Scikit-Learn)
        # -------------------------------------------------------------
        projected_month = 0
        projected_year = 0
        
        if all_logs:
            # Create Pandas DataFrame
            data = []
            for log in all_logs:
                data.append({
                    'date': log.create_date.date(),
                    'tokens': log.tokens_total
                })
            df = pd.DataFrame(data)
            df['date'] = pd.to_datetime(df['date'])
            
            # Group by date
            daily_df = df.groupby('date')['tokens'].sum().reset_index()
            daily_df = daily_df.sort_values('date')
            
            # We need at least 2 days to draw a line
            if len(daily_df) >= 2:
                # Convert dates to ordinal for regression
                daily_df['date_ordinal'] = daily_df['date'].map(datetime.datetime.toordinal)
                
                X = daily_df[['date_ordinal']]
                y = daily_df['tokens']
                
                # Neural Network Model (Redes Neuronales)
                model = MLPRegressor(hidden_layer_sizes=(100, 50), max_iter=1000, random_state=42)
                model.fit(X, y)
                
                # Predict rest of the current month
                remaining_days = days_in_month - days_passed
                future_ordinals = []
                for i in range(1, remaining_days + 1):
                    future_d = today + datetime.timedelta(days=i)
                    future_ordinals.append([future_d.toordinal()])
                
                if future_ordinals:
                    future_preds = model.predict(future_ordinals)
                    # Don't predict negative tokens
                    future_preds = [max(0, p) for p in future_preds]
                    projected_month = total_tokens_month + sum(future_preds)
                else:
                    projected_month = total_tokens_month
                
                # Predict rest of the year
                end_of_year = datetime.date(today.year, 12, 31)
                days_left_year = (end_of_year - today).days
                year_ordinals = []
                for i in range(1, days_left_year + 1):
                    future_d = today + datetime.timedelta(days=i)
                    year_ordinals.append([future_d.toordinal()])
                
                if year_ordinals:
                    year_preds = model.predict(year_ordinals)
                    year_preds = [max(0, p) for p in year_preds]
                    total_year_so_far = sum(all_logs.filtered(lambda l: l.create_date.date().year == today.year).mapped('tokens_total'))
                    projected_year = total_year_so_far + sum(year_preds)
                else:
                    projected_year = total_tokens_month * 12 # Fallback
            else:
                # Fallback to simple math if not enough data for ML
                projected_month = total_tokens_month + (average_daily * (days_in_month - days_passed))
                projected_year = projected_month * 12
        
        projected_month = int(projected_month)
        projected_year = int(projected_year)

        # 2. Line Chart (Yearly - Jan to Dec)
        months_labels = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
        labels_line = months_labels
        data_line_actual = []
        data_line_predicted = []
        
        # Calculate actuals per month
        for m in range(1, 13):
            if m <= today.month:
                logs_m = all_logs.filtered(lambda l: l.create_date.date().year == today.year and l.create_date.date().month == m)
                data_line_actual.append(sum(logs_m.mapped('tokens_total')))
            else:
                data_line_actual.append(None)
                
        # Calculate predictions per month
        for m in range(1, 13):
            if m < today.month:
                # Past months have no prediction
                data_line_predicted.append(None)
            elif m == today.month:
                # Current month = actual so far + predicted rest of month
                data_line_predicted.append(projected_month)
            else:
                # Future months
                import calendar
                _, days_in_m = calendar.monthrange(today.year, m)
                
                if 'model' in locals():
                    m_ordinals = []
                    for d in range(1, days_in_m + 1):
                        m_ordinals.append([datetime.date(today.year, m, d).toordinal()])
                    m_preds = model.predict(m_ordinals)
                    m_preds = [max(0, p) for p in m_preds]
                    data_line_predicted.append(int(sum(m_preds)))
                else:
                    data_line_predicted.append(int(average_daily * days_in_m))

        # 3. Pie Chart (By Module) - use 30 days instead of month so it's never empty
        module_usage = defaultdict(int)
        for log in logs_30_days:
            module = log.module_caller or 'Desconocido'
            module_usage[module] += log.tokens_total
            
        labels_pie = list(module_usage.keys())
        data_pie = list(module_usage.values())

        # Currency Conversion to MXN
        usd_currency = self.env.ref('base.USD', raise_if_not_found=False)
        mxn_currency = self.env.ref('base.MXN', raise_if_not_found=False)
        total_cost_mxn = 0.0
        if usd_currency and mxn_currency:
            total_cost_mxn = usd_currency._convert(total_cost_month, mxn_currency, self.env.company, today)
        else:
            total_cost_mxn = total_cost_month * 18.0 # Fallback

        return {
            'kpis': {
                'total_tokens_month': total_tokens_month,
                'token_limit': token_limit,
                'average_daily': average_daily,
                'projected_month': projected_month,
                'projected_year': projected_year,
                'total_cost_usd': round(total_cost_month, 4),
                'total_cost_mxn': round(total_cost_mxn, 4),
            },
            'charts': {
                'trend': {
                    'labels': labels_line,
                    'data_actual': data_line_actual,
                    'data_predicted': data_line_predicted,
                },
                'modules': {
                    'labels': labels_pie,
                    'data': data_pie,
                }
            }
        }
