/* Minimal MD5 (RFC 1321) for teaching demos. md5(string) → 32-character hex digest of the UTF-8 bytes. */
(function (global) {
  'use strict';
  var S = [7, 12, 17, 22, 7, 12, 17, 22, 7, 12, 17, 22, 7, 12, 17, 22, 5, 9, 14, 20, 5, 9, 14, 20, 5, 9, 14, 20, 5, 9, 14, 20,
           4, 11, 16, 23, 4, 11, 16, 23, 4, 11, 16, 23, 4, 11, 16, 23, 6, 10, 15, 21, 6, 10, 15, 21, 6, 10, 15, 21, 6, 10, 15, 21];
  var K = [];
  for (var i = 0; i < 64; i++) K[i] = (Math.floor(Math.abs(Math.sin(i + 1)) * 4294967296)) | 0;
  function add(x, y) { return (x + y) | 0; }
  function md5(str) {
    var bytes = unescape(encodeURIComponent(str)), n = bytes.length, nblk = ((n + 8) >> 6) + 1, w = new Array(nblk * 16).fill(0), j;
    for (j = 0; j < n; j++) w[j >> 2] |= bytes.charCodeAt(j) << ((j % 4) * 8);
    w[n >> 2] |= 0x80 << ((n % 4) * 8);
    w[nblk * 16 - 2] = (n * 8) | 0;
    w[nblk * 16 - 1] = Math.floor(n * 8 / 4294967296) | 0;
    var a0 = 0x67452301, b0 = 0xefcdab89 | 0, c0 = 0x98badcfe | 0, d0 = 0x10325476;
    for (var b = 0; b < w.length; b += 16) {
      var A = a0, B = b0, C = c0, D = d0, F, g;
      for (j = 0; j < 64; j++) {
        if (j < 16) { F = (B & C) | (~B & D); g = j; }
        else if (j < 32) { F = (D & B) | (~D & C); g = (5 * j + 1) % 16; }
        else if (j < 48) { F = B ^ C ^ D; g = (3 * j + 5) % 16; }
        else { F = C ^ (B | ~D); g = (7 * j) % 16; }
        var tmp = D; D = C; C = B;
        var x = add(add(A, F), add(K[j], w[b + g]));
        B = add(B, (x << S[j]) | (x >>> (32 - S[j])));
        A = tmp;
      }
      a0 = add(a0, A); b0 = add(b0, B); c0 = add(c0, C); d0 = add(d0, D);
    }
    function hex(v) { var h = ''; for (var k = 0; k < 4; k++) h += ('0' + ((v >>> (k * 8)) & 255).toString(16)).slice(-2); return h; }
    return hex(a0) + hex(b0) + hex(c0) + hex(d0);
  }
  global.md5 = md5;
})(typeof window !== 'undefined' ? window : globalThis);
