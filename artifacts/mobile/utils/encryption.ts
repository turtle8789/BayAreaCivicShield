/**
 * AES-256-CBC + PBKDF2-SHA256 + HMAC-SHA256 (Encrypt-then-MAC) helpers.
 *
 * Format v:2 envelope: { v, s, i, c, h }
 *   v — schema version (2)
 *   s — salt (hex, 16 bytes)
 *   i — IV   (hex, 16 bytes)
 *   c — AES-256-CBC ciphertext (Base64)
 *   h — HMAC-SHA256( s‖i‖c , Kmac ) (hex, 32 bytes)
 *
 * Key derivation: PBKDF2-SHA256, 100 000 iterations, 512-bit output.
 *   Kenc = first 256 bits  →  AES-256-CBC encryption key
 *   Kmac = last  256 bits  →  HMAC-SHA256 authentication key
 *
 * Why Encrypt-then-MAC?
 *   AES-CBC alone provides confidentiality but no integrity. An attacker who
 *   can write to the stored backup file could flip ciphertext bits and cause
 *   the app to import silently-corrupted encounter records. The HMAC tag
 *   catches any tampering (and wrong-password attempts) before decryption.
 *
 * CryptoJS.lib.WordArray.random uses Hermes's built-in crypto.getRandomValues
 * (available since Expo 50+) — no native module required.
 */

import CryptoJS from 'crypto-js';

/** Constant-time comparison for hex strings to prevent timing attacks. */
function timingSafeEqual(a: string, b: string): boolean {
  if (a.length !== b.length) return false;
  let diff = 0;
  for (let i = 0; i < a.length; i++) {
    diff |= a.charCodeAt(i) ^ b.charCodeAt(i);
  }
  return diff === 0;
}

/**
 * Encrypts `plaintext` with AES-256-CBC and authenticates with HMAC-SHA256.
 * Returns a JSON string (v:2 envelope) safe to store or embed in HTML.
 */
export function aesEncryptStrong(plaintext: string, password: string): string {
  const saltHex = CryptoJS.lib.WordArray.random(16).toString(CryptoJS.enc.Hex);
  const ivHex   = CryptoJS.lib.WordArray.random(16).toString(CryptoJS.enc.Hex);

  const salt = CryptoJS.enc.Hex.parse(saltHex);
  const iv   = CryptoJS.enc.Hex.parse(ivHex);

  // Derive 512-bit key material: Kenc (first 256 bits) + Kmac (last 256 bits)
  const keyMaterial = CryptoJS.PBKDF2(password, salt, {
    keySize:    512 / 32,  // 16 × 32-bit words = 512 bits
    iterations: 100_000,
    hasher:     CryptoJS.algo.SHA256,
  });
  const kmHex = keyMaterial.toString(CryptoJS.enc.Hex);
  const kenc  = CryptoJS.enc.Hex.parse(kmHex.slice(0, 64));   // 256-bit AES key
  const kmac  = CryptoJS.enc.Hex.parse(kmHex.slice(64, 128)); // 256-bit HMAC key

  const ciphertext    = CryptoJS.AES.encrypt(plaintext, kenc, {
    iv,
    mode:    CryptoJS.mode.CBC,
    padding: CryptoJS.pad.Pkcs7,
  });
  const ciphertextStr = ciphertext.toString(); // Base64

  // Encrypt-then-MAC: sign over salt ‖ iv ‖ ciphertext (all hex/Base64 strings)
  const hmac = CryptoJS.HmacSHA256(saltHex + ivHex + ciphertextStr, kmac)
    .toString(CryptoJS.enc.Hex);

  return JSON.stringify({ v: 2, s: saltHex, i: ivHex, c: ciphertextStr, h: hmac });
}

/**
 * Decrypts a v:2 envelope produced by `aesEncryptStrong`.
 * Returns the plaintext on success, or `null` when:
 *   - the password is wrong (HMAC mismatch)
 *   - the payload is malformed or tampered
 */
export function aesDecryptStrong(encryptedPayload: string, password: string): string | null {
  try {
    const data = JSON.parse(encryptedPayload) as {
      v: number; s: string; i: string; c: string; h: string;
    };
    if (data.v !== 2 || !data.s || !data.i || !data.c || !data.h) return null;

    const salt = CryptoJS.enc.Hex.parse(data.s);

    // Re-derive the same 512-bit key material
    const keyMaterial = CryptoJS.PBKDF2(password, salt, {
      keySize:    512 / 32,
      iterations: 100_000,
      hasher:     CryptoJS.algo.SHA256,
    });
    const kmHex = keyMaterial.toString(CryptoJS.enc.Hex);
    const kenc  = CryptoJS.enc.Hex.parse(kmHex.slice(0, 64));
    const kmac  = CryptoJS.enc.Hex.parse(kmHex.slice(64, 128));

    // Verify MAC *before* decrypting (Encrypt-then-MAC)
    const expectedHmac = CryptoJS.HmacSHA256(data.s + data.i + data.c, kmac)
      .toString(CryptoJS.enc.Hex);
    if (!timingSafeEqual(data.h, expectedHmac)) return null;

    const iv        = CryptoJS.enc.Hex.parse(data.i);
    const decrypted = CryptoJS.AES.decrypt(data.c, kenc, {
      iv,
      mode:    CryptoJS.mode.CBC,
      padding: CryptoJS.pad.Pkcs7,
    });

    const plaintext = decrypted.toString(CryptoJS.enc.Utf8);
    return plaintext || null;
  } catch {
    return null;
  }
}
