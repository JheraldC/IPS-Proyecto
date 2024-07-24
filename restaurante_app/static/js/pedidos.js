document.addEventListener('DOMContentLoaded', (event) => {
  const pedidosCancelados = JSON.parse(document.getElementById('pedidos_cancelados').textContent);
  const pedidosEnProceso = JSON.parse(document.getElementById('pedidos_en_proceso').textContent);
  const pedidosFinalizados = JSON.parse(document.getElementById('pedidos_finalizados').textContent);

  const paginacionFinalizados = document.getElementById('paginacion-finalizados'); // Contenedor para los botones de paginación
  // Variables currentPage para cada tipo de pedido
  let currentPage = 1;
  let currentPageEnProceso = 1;
  let currentPageCancelados = 1;
  let currentPageFinalizados = 1;

  // Llenar las listas de pedidos (con verificación de array)
  function llenarListaPedidos(listaId, pedidos) {
    const lista = document.getElementById(listaId);
    lista.innerHTML = ''; // Limpiar la lista
    const parsedPedidos = JSON.parse(pedidos);

    if (!Array.isArray(parsedPedidos) || parsedPedidos.length === 0) {
      const mensajeVacio = document.createElement('li');
      mensajeVacio.textContent = 'No hay pedidos en esta sección.';
      lista.appendChild(mensajeVacio);
    } else {
      // Filtrar pedidos por estado
      const pedidosFiltrados = parsedPedidos.filter(pedido => {
        if (listaId === 'lista-enproceso' && pedido.EstPedCod_id === 1) return true;
        if (listaId === 'lista-cancelados' && pedido.EstPedCod_id === 2) return true;
        if (listaId === 'lista-finalizados' && pedido.EstPedCod_id === 3) return true;
        return false; // No mostrar si el estado no coincide
      });

      pedidosFiltrados.forEach(pedido => {
        const listItem = document.createElement('li');
        listItem.classList.add('pedido-item-pedidos');
        listItem.dataset.pedidoId = pedido.PedCod; // Agregar un atributo para identificar el pedido

        // Agregar botón "Cancelar" solo si el pedido está en proceso
        if (listaId === 'lista-enproceso') {
          const cancelarButton = document.createElement('button');
          const xbutton = document.createElement('i');
          xbutton.classList.add("fa-solid", "fa-x");
          cancelarButton.classList.add('cancelar-btn');
          cancelarButton.dataset.pedidoId = pedido.PedCod;
          cancelarButton.addEventListener('click', () => cancelarPedido(pedido.PedCod));
          cancelarButton.appendChild(xbutton)
          listItem.appendChild(cancelarButton);
        }

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
          platoSpan.textContent = detalle.MenDes;

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

  // Función para cancelar un pedido
  function cancelarPedido(pedidoId) {
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    fetch(`/cancelar_pedido/${pedidoId}/`, {  // Llamada a la nueva vista
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken
      }
    })
      .then(response => response.json())
      .then(data => {
        if (data.success) {
          // Actualizar la página o la lista de pedidos
          location.reload(); // Recarga la página completa
        } else {
          alert('Error al cancelar el pedido: ' + data.error);
        }
      });
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

  // Función para cargar y mostrar los pedidos de una página (modificada)
  function cargarPedidos(page) {
    const fechaActual = new Date().toISOString().split('T')[0];
    fetch(`/obtener_pedidos_json/?page=${page}&fecha=${fechaActual}`)
      .then(response => response.json())
      .then(data => {
        currentPage = data.page_number; // Actualizar la página actual

        // Llenar las listas de pedidos
        llenarListaPedidos('lista-enproceso', data.pedidos_en_proceso);
        llenarListaPedidos('lista-cancelados', data.pedidos_cancelados);
        llenarListaPedidos('lista-finalizados', data.pedidos_finalizados);

        // Actualizar la paginación para cada tipo de pedido
        actualizarPaginacion('paginacion-enproceso', data.paginacion.pedidos_en_proceso);
        actualizarPaginacion('paginacion-cancelados', data.paginacion.pedidos_cancelados);
        actualizarPaginacion('paginacion-finalizados', data.paginacion.pedidos_finalizados);

        actualizarContadores(data.paginacion); // Actualizar los contadores de pedidos
      })
      .catch(error => {
        console.error('Error al cargar pedidos:', error);
      });
  }

  // Función para actualizar los botones de paginación
  function actualizarPaginacion(containerId, paginacionInfo) {
    const paginacionContainer = document.getElementById(containerId);
    paginacionContainer.innerHTML = ''; // Limpiar los botones existentes

    // Botón "Anterior"
    if (!paginacionInfo) {
      const mensajeVacio = document.createElement('span');
      mensajeVacio.textContent = 'No hay pedidos';
      paginacionContainer.appendChild(mensajeVacio);
      return; // Salir de la función si no hay información de paginación
    }

    if (paginacionInfo.page_number > 1) {
      const prevButton = document.createElement('button');
      prevButton.textContent = 'Anterior';
      prevButton.addEventListener('click', () => cargarPedidos(paginacionInfo.page_number - 1));
      paginacionContainer.appendChild(prevButton);
    }

    // Indicador de página actual
    const currentPageSpan = document.createElement('span');
    currentPageSpan.textContent = `${paginacionInfo.page_number} de ${paginacionInfo.total_pages}`;
    paginacionContainer.appendChild(currentPageSpan);

    // Botón "Siguiente"
    if (paginacionInfo.has_next) {
      const nextButton = document.createElement('button');
      nextButton.textContent = 'Siguiente';
      nextButton.addEventListener('click', () => cargarPedidos(paginacionInfo.page_number + 1));
      paginacionContainer.appendChild(nextButton);
    }
  }

  // Función para actualizar los contadores
  function actualizarContadores(paginacionInfo) {
    // Usar total_pedidos de la información de paginación
    document.getElementById('num-cancelados').textContent = paginacionInfo.pedidos_cancelados.total_pedidos;
    document.getElementById('num-enproceso').textContent = paginacionInfo.pedidos_en_proceso.total_pedidos;
    document.getElementById('num-finalizados').textContent = paginacionInfo.pedidos_finalizados.total_pedidos;
  }
  cargarPedidos(currentPage)

});
