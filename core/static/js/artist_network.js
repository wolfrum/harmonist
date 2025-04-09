document.addEventListener('DOMContentLoaded', () => {
  const graphEl = document.getElementById('artist-network-graph');
  const artistId = graphEl?.dataset?.artistId;

  if (!graphEl || !artistId) {
    console.warn('❌ artist-network-graph container or artistId missing');
    return;
  }

  fetch(`/api/artist/${artistId}/network/`)
    .then((res) => res.json())
    .then(({ nodes, links }) => {
      const width = graphEl.clientWidth;
      const height = graphEl.clientHeight;

      const svg = d3
        .select(graphEl)
        .append('svg')
        .attr('width', width)
        .attr('height', height);

      const container = svg.append('g');
      const defs = svg.append('defs');

      nodes.forEach((node) => {
        if (node.image) {
          defs
            .append('pattern')
            .attr('id', `thumb-${node.id}`)
            .attr('patternUnits', 'objectBoundingBox')
            .attr('width', 1)
            .attr('height', 1)
            .append('image')
            .attr('href', node.image)
            .attr('width', 40)
            .attr('height', 40);
        }
      });

      const link = container
        .append('g')
        .selectAll('line')
        .data(links)
        .join('line')
        .attr('stroke', (d) =>
          d.type === 'influenced' ? '#3b82f6' : '#10b981'
        )
        .attr('stroke-width', 2)
        .attr('stroke-opacity', 0.6);

      const node = container
        .append('g')
        .selectAll('circle')
        .data(nodes)
        .join('circle')
        .attr('r', 20)
        .attr('fill', (d) => (d.image ? `url(#thumb-${d.id})` : '#3b82f6'))
        .attr('stroke', '#333')
        .attr('stroke-width', 1.5)
        .style('cursor', 'pointer')
        .on('click', (event, d) => (window.location.href = d.url));

      const label = container
        .append('g')
        .selectAll('text')
        .data(nodes)
        .join('text')
        .text((d) => d.label)
        .attr('font-size', 12)
        .attr('text-anchor', 'middle')
        .attr('fill', '#111')
        .style('pointer-events', 'none');

      const simulation = d3
        .forceSimulation(nodes)
        .force(
          'link',
          d3
            .forceLink(links)
            .id((d) => d.id)
            .distance(150)
        )
        .force('charge', d3.forceManyBody().strength(-300))
        .force('center', d3.forceCenter(width / 2, height / 2))
        .stop();

      // Manually step the simulation forward a few ticks for initial layout
      for (let i = 0; i < 50; i++) simulation.tick();

      // Position DOM elements once
      link
        .attr('x1', (d) => d.source.x)
        .attr('y1', (d) => d.source.y)
        .attr('x2', (d) => d.target.x)
        .attr('y2', (d) => d.target.y);

      node.attr('cx', (d) => d.x).attr('cy', (d) => d.y);
      label.attr('x', (d) => d.x).attr('y', (d) => d.y + 1.5 * 23);

      // Setup zoom
      const zoom = d3
        .zoom()
        .on('zoom', (event) => container.attr('transform', event.transform));
      svg.call(zoom);

      // Immediately fit the graph to center
      function zoomToFit() {
        if (!nodes.length) return;

        const allX = nodes.map((d) => d.x);
        const allY = nodes.map((d) => d.y);
        const minX = Math.min(...allX);
        const maxX = Math.max(...allX);
        const minY = Math.min(...allY);
        const maxY = Math.max(...allY);

        const padding = 100;
        const boxWidth = Math.max(maxX - minX, 1);
        const boxHeight = Math.max(maxY - minY, 1);

        const scale = Math.min(
          (width - padding) / boxWidth,
          (height - padding) / boxHeight,
          2
        );

        const centerX = (minX + maxX) / 2;
        const centerY = (minY + maxY) / 2;

        const translateX = width / 2 - scale * centerX;
        const translateY = height / 2 - scale * centerY;

        const transform = d3.zoomIdentity
          .translate(translateX, translateY)
          .scale(scale);
        svg
          .transition()
          .duration(400)
          .ease(d3.easeCubicOut)
          .call(zoom.transform, transform);
      }

      // Delay before zoom to allow DOM paint
      setTimeout(() => {
        zoomToFit();
      }, 500);
    });
});
