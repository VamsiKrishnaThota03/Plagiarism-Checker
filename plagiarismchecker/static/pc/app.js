/* Loading state on submit, live character counts and file name display. */
document.addEventListener('DOMContentLoaded', function () {
  document.querySelectorAll('form[data-loading]').forEach(function (form) {
    form.addEventListener('submit', function () {
      const button = form.querySelector('button[type=submit]');
      if (!button) return;
      button.disabled = true;
      button.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>' + form.dataset.loading;
    });
  });

  document.querySelectorAll('textarea[maxlength]').forEach(function (area) {
    const counter = document.querySelector('[data-count-for="' + area.id + '"]');
    if (!counter) return;
    const update = function () { counter.textContent = area.value.length.toLocaleString() + ' / ' + Number(area.maxLength).toLocaleString(); };
    area.addEventListener('input', update);
    update();
  });
});
