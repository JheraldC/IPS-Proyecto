document.addEventListener('DOMContentLoaded', (event) => {
  const pedidosCancelados = JSON.parse(document.getElementById('pedidos_cancelados').textContent);
  const pedidosEnProceso = JSON.parse(document.getElementById('pedidos_en_proceso').textContent);
  const pedidosFinalizados = JSON.parse(document.getElementById('pedidos_finalizados').textContent);

  const listaFinalizados = document.getElementById('lista-finalizados');
  const paginacionFinalizados = document.getElementById('paginacion-finalizados'); // Contenedor para los botones de paginación
  let currentPage = 1;
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

      if (listaId === 'lista-finalizados') {
        // Ordenar los pedidos finalizados por fecha y hora de forma descendente
        pedidosFiltrados.sort((a, b) => {
          const fechaA = new Date(a.PedFec + 'T' + a.PedHor);
          const fechaB = new Date(b.PedFec + 'T' + b.PedHor);
          return fechaB - fechaA; // Orden descendente
        });
      }

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

  // Función para cargar y mostrar los pedidos de una página
  function cargarPedidos(page) {
    const fechaActual = new Date().toISOString().split('T')[0]; // Obtener la fecha actual en formato YYYY-MM-DD
    fetch(`/obtener_pedidos_json/?page=${page}&fecha=${fechaActual}`)
      .then(response => response.json())
      .then(data => {
        llenarListaPedidos('lista-finalizados', data.pedidos_finalizados);
        currentPage = data.page_number;

        // Actualizar botones de paginación (asegurarse de que se llame)
        actualizarPaginacion(data.has_next, data.page_number, data.total_pages);

        document.getElementById('num-finalizados').textContent = data.total_finalizados;
      })
      .catch(error => {
        console.error('Error al cargar pedidos:', error);
        // Manejo de errores en la solicitud fetch (opcional)
      });
  }

  // Función para actualizar los botones de paginación
  function actualizarPaginacion(hasNext, currentPage, totalPages) {
    paginacionFinalizados.innerHTML = ''; // Limpiar los botones existentes

    // Botón "Anterior"
    if (currentPage > 1) {
      const prevButton = document.createElement('button');
      prevButton.textContent = 'Anterior';
      prevButton.addEventListener('click', () => cargarPedidos(currentPage - 1));
      paginacionFinalizados.appendChild(prevButton);
    }

    // Indicador de página actual
    const currentPageSpan = document.createElement('span');
    currentPageSpan.textContent = `${currentPage} de ${totalPages}`;
    paginacionFinalizados.appendChild(currentPageSpan);

    // Botón "Siguiente"
    if (hasNext) {
      const nextButton = document.createElement('button');
      nextButton.textContent = 'Siguiente';
      nextButton.addEventListener('click', () => cargarPedidos(currentPage + 1));
      paginacionFinalizados.appendChild(nextButton);
    }
  }

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
  cargarPedidos(currentPage)

});
