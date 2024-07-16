document.addEventListener('DOMContentLoaded', (event) => {
  const mesaNumero = document.querySelector('.container').dataset.mesaNumero;
  const menuItems = document.querySelectorAll('.menu-item');
  const pedidoItems = document.getElementById('lista-pedido');
  const totalAmount = document.getElementById('total-amount');
  const finalizarVentaButton = document.getElementById('finalizar-venta');
  const categoriaBtns = document.querySelectorAll('.categoria-btn');

  let pedido = {};

  // Obtén los platos desde el JSON
  const platos = window.platos;
  const pedidosCancelados = JSON.parse(document.getElementById('pedidos_cancelados').textContent);
  const pedidosEnProceso = JSON.parse(document.getElementById('pedidos_en_proceso').textContent);
  const pedidosFinalizados = JSON.parse(document.getElementById('pedidos_finalizados').textContent);

  // Llena las listas de pedidos (con verificación de array)
  llenarListaPedidos('lista-cancelados', pedidosCancelados);
  llenarListaPedidos('lista-enproceso', pedidosEnProceso);
  llenarListaPedidos('lista-finalizados', pedidosFinalizados);
  actualizarContadores();


  // Llenar las listas de pedidos (con verificación de array)
  function llenarListaPedidos(listaId, pedidos) {
    const lista = document.getElementById(listaId);
    lista.innerHTML = ''; // Limpiar la lista

    if (!Array.isArray(pedidos) || pedidos.length === 0) {
      const mensajeVacio = document.createElement('li');
      mensajeVacio.textContent = 'No hay pedidos en esta sección.';
      lista.appendChild(mensajeVacio);
    } else {
      // Filtrar pedidos por estado
      const pedidosFiltrados = pedidos.filter(pedido => {
        if (listaId === 'lista-enproceso' && pedido.EstPedCod_id === 1) return true;
        if (listaId === 'lista-cancelados' && pedido.EstPedCod_id === 2) return true;
        if (listaId === 'lista-finalizados' && pedido.EstPedCod_id === 3) return true;
        return false; // No mostrar si el estado no coincide
      });

      pedidosFiltrados.forEach(pedido => {
        const listItem = document.createElement('li');
        listItem.classList.add('pedido-item');
        listItem.dataset.pedidoId = pedido.PedCod; // Agregar un atributo para identificar el pedido

        // Detalles del pedido (Mesa, Observaciones, Total.mesa)
        const mesaDiv = document.createElement('div');
        mesaDiv.classList.add('mesa-item');
        mesaDiv.textContent = `Mesa: ${pedido.MesCod_id}`;

        const observacionesDiv = document.createElement('div');
        observacionesDiv.classList.add('observaciones');
        observacionesDiv.textContent = `Observaciones: ${pedido.PedObs || ''}`;

        const totalDiv = document.createElement('div');
        totalDiv.classList.add('total');
        totalDiv.textContent = `Total: S/. ${pedido.PedTot}`;

        listItem.appendChild(mesaDiv);
        listItem.appendChild(observacionesDiv);
        listItem.appendChild(totalDiv);

        // Lista de detalles del pedido (si existen)
        const detallesList = document.createElement('ul');
        pedido.DetPed.forEach(detalle => {
          const detalleItem = document.createElement('li');

          // Agregar clases a cantidad y plato
          const cantidadSpan = document.createElement('span');
          cantidadSpan.classList.add('cantidad');
          cantidadSpan.textContent = `${detalle.PedCan} x `;

          const platoSpan = document.createElement('span');
          platoSpan.classList.add('plato');
          platoSpan.textContent = detalle.MenCod__MenDes;

          detalleItem.appendChild(cantidadSpan);
          detalleItem.appendChild(platoSpan);
          detallesList.appendChild(detalleItem);
        });
        listItem.appendChild(detallesList);

        // Agregar botón "Siguiente" solo si el pedido está en proceso
        if (listaId === 'lista-enproceso') {
          const siguienteButton = document.createElement('button');
          siguienteButton.textContent = 'Siguiente';
          siguienteButton.classList.add('siguiente-btn');
          siguienteButton.dataset.pedidoId = pedido.PedCod;
          listItem.appendChild(siguienteButton);
        }

        lista.appendChild(listItem);
      });
    }
  }

  document.addEventListener('click', function(event) {
    const csrfTokenInput = document.querySelector('input[name="csrfmiddlewaretoken"]');
    const csrfToken = csrfTokenInput.value;
    if (event.target.classList.contains('siguiente-btn')) {
      const pedidoId = event.target.dataset.pedidoId;
      fetch(`/actualizar_estado_pedido/${pedidoId}/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken,
        }
      })
        .then(response => response.json())
        .then(data => {
          if (data.success) {
            location.reload();
          } else {
            alert('Error al actualizar el estado del pedido: ' + data.error);
          }
        });
    }
  });

  // Manejar clics en los botones "Eliminar"
  document.addEventListener('click', (event) => {
    if (event.target.classList.contains('eliminar-plato')) {
      const listItem = event.target.closest('.pedido-item');
      const platoId = listItem.dataset.detalleId;
      // Eliminar el plato del pedido en memoria
      delete pedido[platoId];
      // Eliminar el elemento de la lista del DOM
      listItem.remove();
      // Actualizar el total del pedido
      actualizarPedido();
      // Reiniciar la cantidad en el contenedor .cantidad-container del plato correspondiente
      const menuItem = document.querySelector(`.menu-item[data-plato-id="${platoId}"]`);
      if (menuItem) {
        const cantidadSpan = menuItem.querySelector('.cantidad');
        cantidadSpan.textContent = 0;
      }
    }
  });

  // Función para actualizar los contadores
  function actualizarContadores() {
    const numCancelados = Array.from(document.getElementById('lista-cancelados').children)
      .filter(child => child.textContent !== 'No hay pedidos en esta sección.')
      .length;

    const numEnProceso = Array.from(document.getElementById('lista-enproceso').children)
      .filter(child => child.textContent !== 'No hay pedidos en esta sección.')
      .length;

    const numFinalizados = Array.from(document.getElementById('lista-finalizados').children)
      .filter(child => child.textContent !== 'No hay pedidos en esta sección.')
      .length;

    document.getElementById('num-cancelados').textContent = numCancelados;
    document.getElementById('num-enproceso').textContent = numEnProceso;
    document.getElementById('num-finalizados').textContent = numFinalizados;
  }

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


  // Manejar clics en los botones "+" y "-" de la lista de platos
  document.querySelector('.menu-items').addEventListener('click', (event) => {
    if (event.target.matches('.btn-cantidad')) {
      const menuItem = event.target.closest('.menu-item');

      if (menuItem !== null) {  // Verificar si menuItem existe
        const platoId = menuItem.dataset.platoId;
        const action = event.target.dataset.action;
        const cantidadSpan = menuItem.querySelector('.cantidad');
        let cantidad = parseInt(cantidadSpan.textContent);

        if (action === 'sumar') {
          cantidad++;
        } else if (action === 'restar' && cantidad > 0) {
          cantidad--;
        }

        cantidadSpan.textContent = cantidad;
        pedido[platoId] = cantidad; // Actualizar el pedido en memoria

        actualizarPedido();
      }
    }
  });

  // Manejar clics en los botones "+" y "-" dentro de la lista de pedido
  pedidoItems.addEventListener('click', (event) => {
    if (event.target.classList.contains('btn-cantidad')) {
      const listItem = event.target.closest('.pedido-item');

      if (listItem) {
        const detalleId = listItem.dataset.detalleId;
        const action = event.target.dataset.action;
        const cantidadSpanPedido = listItem.querySelector('.cantidad');
        const precioSpan = listItem.querySelector('.pedido-item-precio');
        let cantidad = parseInt(cantidadSpanPedido.textContent);
        const precioUnitario = parseFloat(precioSpan.textContent.replace('S/', ''));

        if (action === 'sumar') {
          cantidad++;
        } else if (action === 'restar' && cantidad > 0) {
          cantidad--;
        }

        cantidadSpanPedido.textContent = cantidad;
        precioSpan.textContent = `S/${(precioUnitario * cantidad).toFixed(2)}`;

        // Actualiza la cantidad en el objeto 'pedido'
        pedido[detalleId] = cantidad;

        // Actualiza la cantidad en el elemento del menú correspondiente
        const menuItem = document.querySelector(`.menu-item[data-plato-id="${detalleId}"]`);
        if (menuItem) {
          const cantidadSpanMenu = menuItem.querySelector('.cantidad');
          cantidadSpanMenu.textContent = cantidad;
        }

        actualizarPedido();
      }
    }
  });

  // Actualizar el total del pedido
  function actualizarPedido() {
    const pedidoItems = document.getElementById('lista-pedido'); // Obtén el elemento nuevamente
    if (pedidoItems) { // Verifica si existe
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
  }

  // Enviar el pedido al servidor (AJAX)
  finalizarVentaButton.addEventListener('click', () => {
    const csrfTokenInput = document.querySelector('input[name="csrfmiddlewaretoken"]');
    const csrfToken = csrfTokenInput.value;
    fetch(`/mesas/${mesaNumero}/detalle-pedido/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken,
        'X-Requested-With': 'XMLHttpRequest'
      },
      body: JSON.stringify({ platos: pedido, finalizar_venta: true })
    })
      .then(response => response.json())
      .then(data => {
        if (data.success) {
          window.location.href = data.redirect_url;
        } else {
          alert('Error al realizar el pedido: ' + data.error);
        }
      });
  });

});

