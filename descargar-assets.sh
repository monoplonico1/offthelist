#!/usr/bin/env bash
# Descarga las imágenes del Figma "Off the List" (frame 24:1837) a ./assets.
# Las URLs las genera el MCP de Figma y caducan a los 7 días (emitidas el 2026-09-30).
# Si ya caducaron, vuelve a pedir el design context del nodo y actualiza los IDs.
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p assets
B=https://www.figma.com/api/mcp/asset
while read -r archivo id; do
  [ -z "$archivo" ] && continue
  echo "→ $archivo"
  curl -fsSL -o "assets/$archivo" "$B/$id"
done <<'LISTA'
brand.svg 27adac74-b872-4774-8669-5718eccbcb6e.svg
grid-lines.svg 023eacce-26aa-4e25-8512-4af38e4cb0a3.svg
hero-circle.svg ad82dc63-7743-490d-86a0-ad68db1d390e.svg
hero-traveller.png abd45e84-fe85-4bf7-8c28-fade1d50f216.png
marker.svg 246aaa78-c349-4d87-aef8-4c844b563a4e.svg
marker-white.svg ed931724-90c7-49d1-9300-b175fd4d9389.svg
mask-blob.svg df210091-c1c0-462f-9a72-dbee5fc089d7.svg
mask-blob-2.svg e74acd1c-2b04-45ff-860c-6e8de8657b2f.svg
mask-traveller.svg 22fa757d-2837-4df1-b473-be0abb30000c.svg
how-1.png 2757ecb4-562f-4cce-97cb-61872686b099.png
how-2.png e3256884-e78a-4e14-b1bc-c0ba97e868fa.png
step-1.png 126ec203-3689-45d6-9359-2f94b16b6a65.png
step-2.png 4121df97-60b4-4ec2-9c13-a01aae004522.png
step-3.png a12c2485-b081-4f10-a7b2-34612e9ac53d.png
mystery-traveller.png b036c81b-00fa-4856-bf12-d36d38278c3d.png
line.svg e235cf35-5e24-40bf-a43f-ac6cd484cbd1.svg
pillars.png 94b4e399-c0e2-4e8f-8d9f-ee0d0655ec78.png
dot.svg 9270189d-59dc-4c64-8f63-cda372c05412.svg
guide.png 91bdafbd-c46a-465a-8baa-60cedfe60660.png
gallery-0.png 548bab14-076d-41ab-8912-f7808570e7f1.png
gallery-1.png ecb57f98-9fb2-48c4-8e9f-5317f21d6183.png
gallery-2.png ef2fc63e-f41d-4638-88a7-5f3ad16d954d.png
gallery-3.png 5e9e980f-5db8-45be-bccb-872b3914322c.png
gallery-4.png 7b3eb710-c92c-4c22-9491-e66deccf09f5.png
gallery-5.png 90896299-df1b-40c9-ae35-e3608fbd6c06.png
gallery-6.png 4d5e10df-c101-4dfa-8a28-482261eaeaa1.png
gallery-7.png 37b3704b-a3b2-483d-9da6-8250a9a1bf63.png
gallery-8.png bd2f4359-1752-4091-8ef5-15ac275867ff.png
gallery-9.png 809c823a-5004-483e-a646-6d0d65e91e76.png
gallery-10.png b3322996-901e-476a-b3de-65447634ab95.png
gallery-11.png 0cf7cba6-f047-4a67-9277-0c712b923b0c.png
gallery-12.png d7339f78-d4ec-4281-9b18-bc8237165805.png
testimonial-vanessa.png eee73a85-8b86-4bb9-9d31-f085c81d10eb.png
stars.svg 0d7d9496-d8eb-4b00-bcac-8704c2b1b750.svg
dots.svg 53b1be1d-d2c9-427a-9925-5e1d3909a7c0.svg
footer-wave.svg d47d99d5-de6c-4770-b6fc-57a6743b3abf.svg
instagram.svg 5046b6de-cc27-48e5-aeda-1b57bf54ea96.svg
facebook.svg a17556b3-ac66-4aa1-9b39-33248a6bf50b.svg
twitter.svg c22e6dc9-8393-4790-bfbf-479d027f444c.svg
youtube.svg 3e6590ed-06a9-44dd-a185-1e1bd302b1de.svg
LISTA
echo "Listo: $(ls assets | wc -l) archivos en assets/"
