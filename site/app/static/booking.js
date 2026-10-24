(function () {
  'use strict';

  var form = document.querySelector('[data-wizard]');
  if (!form) return;

  var steps = Array.prototype.slice.call(form.querySelectorAll('[data-step]'));
  if (!steps.length) return;
  var progress = form.querySelector('[data-progress]');
  var live = form.querySelector('[data-live]');
  var recap = form.querySelector('[data-recap]');
  var recapFallback = form.querySelector('[data-recap-fallback]');
  var submitBtn = form.querySelector('[data-submit]');
  var current = 0;

  function stepTitles() {
    return steps.map(function (step) {
      var title = step.querySelector('.step-title');
      return title ? title.textContent.replace(/^\s*\d+\s*/, '').trim() : '';
    });
  }

  function buildProgress() {
    if (!progress) return;
    progress.innerHTML = '';
    steps.forEach(function (step, index) {
      var item = document.createElement('li');
      item.textContent = String(index + 1);
      if (index === current) item.setAttribute('aria-current', 'step');
      progress.appendChild(item);
    });
  }

  function show(index, focusHeading) {
    current = Math.max(0, Math.min(index, steps.length - 1));
    steps.forEach(function (step, i) {
      if (i === current) {
        step.setAttribute('data-active', 'true');
      } else {
        step.removeAttribute('data-active');
      }
    });
    buildProgress();
    if (current === steps.length - 1) buildRecap();
    if (live) {
      var titles = stepTitles();
      live.textContent = 'Étape ' + (current + 1) + ' sur ' + steps.length + ' : ' + titles[current];
    }
    if (focusHeading) {
      var heading = steps[current].querySelector('.step-title');
      if (heading) {
        heading.setAttribute('tabindex', '-1');
        heading.focus({ preventScroll: true });
      }
      steps[current].scrollIntoView({ block: 'start', behavior: 'smooth' });
    }
  }

  function fieldsOf(step) {
    return Array.prototype.slice.call(
      step.querySelectorAll('input, select, textarea')
    ).filter(function (field) {
      return field.type !== 'hidden' && !field.disabled;
    });
  }

  function validateStep(index) {
    var fields = fieldsOf(steps[index]);
    for (var i = 0; i < fields.length; i += 1) {
      if (!fields[i].checkValidity()) {
        fields[i].reportValidity();
        return false;
      }
    }
    return true;
  }

  function selectedText(selector) {
    var field = form.querySelector(selector);
    if (!field || !field.value) return '';
    if (field.options && field.selectedIndex >= 0) {
      return field.options[field.selectedIndex].text.trim();
    }
    return field.value;
  }

  function buildRecap() {
    if (!recap) return;
    var rows = [];
    var choice = form.querySelector('input[name="choice"]:checked');
    if (choice) rows.push(['Prestation', choice.getAttribute('data-label') || choice.value]);

    var options = Array.prototype.slice
      .call(form.querySelectorAll('input[name="options"]:checked'))
      .map(function (input) { return input.getAttribute('data-label') || input.value; });
    if (options.length) rows.push(['Options', options.join(', ')]);

    var type = selectedText('select[name="vehicle_type"]');
    var model = (form.querySelector('input[name="vehicle_model"]') || {}).value || '';
    rows.push(['Véhicule', [type, model.trim()].filter(Boolean).join(' — ') || 'Non renseigné']);

    var day = selectedText('select[name="preferred_date"]');
    var slot = form.querySelector('input[name="preferred_time"]:checked');
    rows.push([
      'Créneau souhaité',
      [day, slot ? slot.getAttribute('data-label') : ''].filter(Boolean).join(' à ') ||
        'Non renseigné',
    ]);

    var name = (form.querySelector('input[name="name"]') || {}).value || '';
    var email = (form.querySelector('input[name="email"]') || {}).value || '';
    var phone = (form.querySelector('input[name="phone"]') || {}).value || '';
    var notes = (form.querySelector('textarea[name="notes"]') || {}).value || '';
    rows.push(['Nom', name.trim() || 'Non renseigné']);
    rows.push(['E-mail', email.trim() || 'Non renseigné']);
    rows.push(['Téléphone', phone.trim() || 'Non renseigné']);
    if (notes.trim()) rows.push(['Remarques', notes.trim()]);

    recap.innerHTML = '';
    rows.forEach(function (row) {
      var wrapper = document.createElement('div');
      var dt = document.createElement('dt');
      dt.textContent = row[0];
      var dd = document.createElement('dd');
      dd.textContent = row[1];
      wrapper.appendChild(dt);
      wrapper.appendChild(dd);
      recap.appendChild(wrapper);
    });
    if (recapFallback) recapFallback.hidden = true;
  }

  form.addEventListener('click', function (event) {
    var next = event.target.closest('[data-next]');
    if (next) {
      if (validateStep(current)) show(current + 1, true);
      return;
    }
    var back = event.target.closest('[data-back]');
    if (back) show(current - 1, true);
  });

  form.addEventListener('submit', function (event) {
    if (current < steps.length - 1) {
      event.preventDefault();
      if (validateStep(current)) show(current + 1, true);
      return;
    }
    if (submitBtn) {
      submitBtn.disabled = true;
      submitBtn.textContent = 'Envoi en cours…';
    }
  });

  form.classList.add('wizard-ready');

  var firstStep = parseInt(form.getAttribute('data-open-step') || '1', 10);
  show(isNaN(firstStep) ? 0 : firstStep - 1, false);

  var summary = document.getElementById('error-summary');
  if (summary) {
    summary.focus();
    summary.scrollIntoView({ block: 'center' });
  }
})();
