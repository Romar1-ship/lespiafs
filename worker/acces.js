// L'identité vient du jeton signé de Cloudflare Access (Cf-Access-Jwt-Assertion), vérifié ici :
// un en-tête d'email seul se falsifie, la signature non. Repris du moteur Atelier (LCCA-studio/atelier).
// En local seulement, MODE=dev prend l'email de DEV_EMAIL.

function b64url(s) {
  s = s.replace(/-/g, "+").replace(/_/g, "/");
  while (s.length % 4) s += "=";
  return Uint8Array.from(atob(s), c => c.charCodeAt(0));
}
const texte = b => new TextDecoder().decode(b);

let certs = null, certsLus = 0;
async function cles(team) {
  if (certs && Date.now() - certsLus < 3600e3) return certs;
  const r = await fetch(`https://${team}/cdn-cgi/access/certs`);
  if (!r.ok) throw new Error("certificats Access " + r.status);
  certs = (await r.json()).keys || [];
  certsLus = Date.now();
  return certs;
}

export async function identite(request, env) {
  if (env.MODE === "dev") return String(env.DEV_EMAIL || "").toLowerCase();
  const jwt = request.headers.get("cf-access-jwt-assertion");
  if (!jwt || !env.ACCESS_TEAM || !env.ACCESS_AUD) return "";
  const [h, p, s] = jwt.split(".");
  if (!h || !p || !s) return "";
  const entete = JSON.parse(texte(b64url(h)));
  const charge = JSON.parse(texte(b64url(p)));
  const aud = Array.isArray(charge.aud) ? charge.aud : [charge.aud];
  if (!aud.includes(env.ACCESS_AUD)) return "";
  if (charge.iss !== `https://${env.ACCESS_TEAM}`) return "";
  if (!charge.exp || charge.exp * 1000 < Date.now()) return "";
  const jwk = (await cles(env.ACCESS_TEAM)).find(k => k.kid === entete.kid);
  if (!jwk) return "";
  const cle = await crypto.subtle.importKey("jwk", jwk, { name: "RSASSA-PKCS1-v1_5", hash: "SHA-256" }, false, ["verify"]);
  const ok = await crypto.subtle.verify("RSASSA-PKCS1-v1_5", cle, b64url(s), new TextEncoder().encode(h + "." + p));
  return ok ? String(charge.email || "").toLowerCase() : "";
}

export function profil(email, env) {
  const valideurs = String(env.VALIDEURS || "").toLowerCase().split(",").map(x => x.trim()).filter(Boolean);
  let m = {};
  try { m = JSON.parse(env.MEMBRES || "{}"); } catch {}
  const nom = Object.entries(m).find(([k]) => k.toLowerCase() === email)?.[1] || email.split("@")[0];
  return { email, nom, valideur: valideurs.includes(email) };
}
