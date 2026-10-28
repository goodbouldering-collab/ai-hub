// Workers TextDecoder supports the Japanese encodings used by the public audit.
// Keep the Node-only audit's iconv interface when bundling for Cloudflare.
export default {
  decode(bytes, encoding) { return new TextDecoder(encoding).decode(bytes); },
  encodingExists(encoding) { try { new TextDecoder(encoding); return true; } catch { return false; } },
};
