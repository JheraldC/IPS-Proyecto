document.addEventListener('DOMContentLoaded', (event) => {
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
        listItem.classList.add('pedido-item-pedidos');
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
});
