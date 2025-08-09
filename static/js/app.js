// Auto-hide bootstrap toasts after 3s
document.querySelectorAll('.toast').forEach(t => {
  const toast = new bootstrap.Toast(t, { delay: 3000 });
  toast.show();
});

// Qty stepper on product detail
document.querySelectorAll('.qty-stepper').forEach(group => {
  const input = group.querySelector('input[type="number"]');
  group.querySelectorAll('button[data-step]').forEach(btn => {
    btn.addEventListener('click', () => {
      const step = parseInt(btn.getAttribute('data-step'), 10);
      const next = Math.max(1, (parseInt(input.value || '1',10) + step));
      input.value = next;
    });
  });
});

// Star rating input
document.querySelectorAll('.rating-input').forEach(container => {
  const name = container.dataset.name || 'rating';
  const hidden = container.parentElement.querySelector(`input[name="${name}"]`);
  const current = parseInt(container.dataset.value || '5', 10);
  container.innerHTML = Array.from({length:5}, (_,i) =>
    `<i class="bi ${i < current ? 'bi-star-fill active':'bi-star'}"></i>`
  ).join('');
  container.querySelectorAll('i').forEach((star, idx) => {
    star.addEventListener('click', () => {
      const val = idx + 1;
      hidden.value = val;
      container.querySelectorAll('i').forEach((s, j) => {
        s.classList.toggle('bi-star-fill', j < val);
        s.classList.toggle('bi-star', j >= val);
        s.classList.toggle('active', j < val);
      });
    });
  });
});
