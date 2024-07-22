document.addEventListener('DOMContentLoaded', () => {
  const limpiarMesaButton = document.getElementById('limpiar-mesa');
  // Manejar clic en el botón "Limpiar"
  if (limpiarMesaButton) {
    limpiarMesaButton.addEventListener('click', function(event) {
      console.log('Clic en el botón Limpiar');
      const csrfTokenInput = document.querySelector('input[name="csrfmiddlewaretoken"]');
      const csrfToken = csrfTokenInput.value;
      const mesaId = event.target.dataset.mesaId;

      fetch(`/limpiar_mesa/${mesaId}/`, {
        method: 'POST',
        headers: {
          'X-CSRFToken': csrfToken,
        }
      })
        .then(response => response.json())
        .then(data => {
          if (data.success) {
            location.reload(); // Recargar la página para reflejar los cambios
          } else {
            alert('Error al limpiar la mesa: ' + data.error);
          }
        });
    });
  }
});

