/** @odoo-module **/

document.addEventListener('DOMContentLoaded', function () {
    const toggleBtn = document.querySelector('.geco_pwd_toggle_btn');
    const pwdInput = document.querySelector('#password');

    if (toggleBtn && pwdInput) {
        toggleBtn.addEventListener('click', function (e) {
            e.preventDefault();
            const icon = toggleBtn.querySelector('i');
            if (pwdInput.type === 'password') {
                pwdInput.type = 'text';
                if (icon) {
                    icon.classList.remove('fa-eye');
                    icon.classList.add('fa-eye-slash');
                }
            } else {
                pwdInput.type = 'password';
                if (icon) {
                    icon.classList.remove('fa-eye-slash');
                    icon.classList.add('fa-eye');
                }
            }
        });
    }
});
