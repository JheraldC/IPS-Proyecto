document.addEventListener('DOMContentLoaded', (event) => {
  const mesaNumero = document.querySelector('.container').dataset.mesaNumero;
  const csrfToken = "{{ csrf_token }}";

  const menuItems = document.querySelectorAll('.menu-item');
  const pedidoItems = document.getElementById('lista-pedido');
  const totalAmount = document.getElementById('total-amount');
  const finalizarVentaButton = document.getElementById('finalizar-venta');
  const categoriaBtns = document.querySelectorAll('.categoria-btn');

  let pedido = {};

  // Obtén los platos desde el JSON
  const platos = window.platos;

  // Filtrar platos por categoría
  categoriaBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const categoria = btn.dataset.categoria;
      categoriaBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');

      menuItems.forEach(item => {
        const platoCategoria = item.dataset.categoria; // Obtener la categoría del atributo data-categoria
        if (categoria === 'todos' || platoCategoria === categoria) {
          item.style.display = 'block';
        } else {
          item.style.display = 'none';
        }
      });
    });
  });

  // Manejar clics en los botones "+" y "-"
  document.addEventListener('click', (event) => {
    if (event.target.classList.contains('btn-cantidad')) {
      const menuItemId = event.target.closest('.menu-item').dataset.platoId;
      const action = event.target.dataset.action;
      const cantidadSpan = event.target.closest('.cantidad-container').querySelector('.cantidad');
      let cantidad = parseInt(cantidadSpan.textContent);

      if (action === 'sumar') {
        cantidad++;
      } else if (action === 'restar' && cantidad > 0) {
        cantidad--;
      }

      cantidadSpan.textContent = cantidad;
      pedido[menuItemId] = cantidad; // Actualiza el pedido en memoria

      actualizarPedido();
    }
  });

  // Actualizar el total del pedido
  function actualizarPedido() {
    pedidoItems.innerHTML = ''; // Limpiar la lista antes de actualizar
    let total = 0;

    for (const platoId in pedido) {
      const cantidad = pedido[platoId];
      if (cantidad > 0) { // Solo agregar si la cantidad es mayor a 0
        const plato = platos.find(p => p.pk == platoId);
        const listItem = document.createElement('li');
        listItem.classList.add('pedido-item');
        listItem.dataset.detalleId = platoId; // Asigna el ID del plato al elemento de la lista

        listItem.innerHTML = `
                    <div class="pedido-item-nombre">${plato.fields.MenDes}</div>
                    <div class="pedido-item-cantidad">
                        <button class="btn-cantidad" data-action="restar" data-plato-id="${platoId}">-</button>
                        <span class="cantidad">${cantidad}</span>
                        <button class="btn-cantidad" data-action="sumar" data-plato-id="${platoId}">+</button>
                    </div>
                    <div class="pedido-item-precio">S/${(plato.fields.precio * cantidad).toFixed(2)}</div>
                    <button class="eliminar-plato" data-plato-id="${platoId}">🗑️</button>
                `;
        pedidoItems.appendChild(listItem);
        total += plato.fields.precio * cantidad;
      }
    }
    totalAmount.textContent = total.toFixed(2);
  }

  // Enviar el pedido al servidor (AJAX)
  finalizarVentaButton.addEventListener('click', () => {
    fetch(`/mesas/${mesaNumero}/detalle-pedido/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken,
        'X-Requested-With': 'XMLHttpRequest'
      },
      body: JSON.stringify({ platos: pedido })
    })
      .then(response => response.json())
      .then(data => {
        if (data.success) {
          // Redirigir a la página de éxito o mostrar un mensaje
          alert('Pedido realizado con éxito');
          // Puedes agregar aquí lógica para actualizar la interfaz o redirigir a otra página
        } else {
          alert('Error al realizar el pedido: ' + data.error);
        }
      });
  });
});

