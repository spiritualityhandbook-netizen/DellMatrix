# Smith Map in DellMatrix

Inspired by Veritasium: *The Scariest Chart in Electrical Engineering* (Smith Chart).

## What we borrowed (structural, not RF hardware claims)

1. **Mismatch creates reflection** — weak or noisy connection when two nodes don't "match"
2. **Match → clean flow** — reduce reflection so ideas transfer without bounce-back
3. **Infinity inside a finite circle** — unit-circle map for phone / Flower viewport
4. **Every point holds two values** — impedance-like flow resistance AND reflection strength (dual, like Dual Lattice)
5. **Stub** — small corrective branch that cancels mismatch without killing the main line
6. **Standing waves** — residue left when mismatch stays high (stored in stigmergic wave lane)

## Files

- `src/core/smith_map.js`
- `src/snapins/smith_pack.js`

## Use

```js
dm.snapIn('smith-pack');
const result = dm.getSnapIn('smith-pack').api.match(dm, nodeA.id, nodeB.id);
console.log(result.flowQuality, result.stub);
```
