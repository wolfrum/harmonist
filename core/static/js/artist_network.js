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
        .attr('height', height)
        .append('g'); // Group for zoom

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

      const link = svg
        .append('g')
        .attr('class', 'links')
        .selectAll('line')
        .data(links)
        .join('line')
        .attr('stroke', (d) => '#60a5fa')
        .attr('stroke-width', 2)
        .attr('stroke-opacity', 0.4)
        .on('mouseover', function () {
          d3.select(this)
            .transition()
            .duration(150)
            .attr('stroke-opacity', 1)
            .attr('stroke-width', 3);
        })
        .on('mouseout', function () {
          d3.select(this)
            .transition()
            .duration(150)
            .attr('stroke-opacity', 0.4)
            .attr('stroke-width', 2);
        })
        .on('click', (event, d) => {
          if (d.url) window.open(d.url, '_blank');
        });

      const node = svg
        .append('g')
        .attr('class', 'nodes')
        .selectAll('circle')
        .data(nodes)
        .join('circle')
        .attr('r', 20)
        .attr('fill', (d) => (d.image ? `url(#thumb-${d.id})` : '#3b82f6'))
        .attr('stroke', '#333')
        .attr('stroke-width', 1.5)
        .style('cursor', 'pointer')
        .on('click', (event, d) => (window.location.href = d.url));

      const label = svg
        .append('g')
        .selectAll('text')
        .data(nodes)
        .join('text')
        .text((d) => d.label)
        .attr('font-size', 12)
        .attr('text-anchor', 'middle')
        .attr('dy', 34) // more spacing
        .attr('fill', '#111')
        .style('pointer-events', 'none');

      const container = d3.select(graphEl).select('svg');
      const zoom = d3.zoom().on('zoom', (event) => {
        svg.attr('transform', event.transform);
      });
      container.call(zoom);

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
        .on('tick', () => {
          link
            .attr('x1', (d) => d.source.x)
            .attr('y1', (d) => d.source.y)
            .attr('x2', (d) => d.target.x)
            .attr('y2', (d) => d.target.y);
          node.attr('cx', (d) => d.x).attr('cy', (d) => d.y);
          label.attr('x', (d) => d.x).attr('y', (d) => d.y);
        });

      // ✅ Apply zoom after a short delay
      setTimeout(() => {
        const allX = nodes.map((d) => d.x);
        const allY = nodes.map((d) => d.y);
        const minX = Math.min(...allX);
        const maxX = Math.max(...allX);
        const minY = Math.min(...allY);
        const maxY = Math.max(...allY);

        const padding = 100;
        const graphWidth = Math.max(maxX - minX, 1);
        const graphHeight = Math.max(maxY - minY, 1);

        const scale = Math.min(
          width / (graphWidth + padding),
          height / (graphHeight + padding),
          2
        );
        const translateX = width / 2 - (scale * (minX + maxX)) / 2;
        const translateY = height / 2 - (scale * (minY + maxY)) / 2;

        container
          .transition()
          .duration(400)
          .call(
            zoom.transform,
            d3.zoomIdentity.translate(translateX, translateY).scale(scale)
          );
      }, 200); // 🧠 Runs faster but still smooth
    });
});
