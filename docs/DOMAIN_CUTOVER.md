# Domain cutover runbook — `opendriveclipboard.com`

Pre-staged commands for moving the Cloud Run service `opendrive-clipboard-demo` from the auto-assigned `*.run.app` URL to the branded apex. Run them top to bottom. Each step lists its precondition — don't skip ahead, the later commands will fail if earlier preconditions aren't met.

Constants:

```bash
PROJECT=opendrive-clipboard
REGION=us-central1
SERVICE=opendrive-clipboard-demo
APEX=opendriveclipboard.com
ORPHAN=clipboard.streetlawopendrive.com
```

---

## Step 0 — Confirm TXT verification propagated

**Precondition:** Added the `google-site-verification=...` TXT record at Network Solutions for `opendriveclipboard.com` (host `@`) AND clicked Verify in Search Console (signed in as `mrlaw@streetlawopendrive.com`).

```bash
dig +short TXT opendriveclipboard.com | grep google-site-verification
```

Expect: one line that includes `google-site-verification=<long-random-string>`. If empty, TXT hasn't propagated yet — wait 2-5 min and retry.

---

## Step 1 — Create the apex domain mapping

**Precondition:** Step 0 passed AND Search Console shows the domain as Verified.

```bash
gcloud beta run domain-mappings create \
  --service=$SERVICE \
  --domain=$APEX \
  --region=$REGION \
  --project=$PROJECT
```

Output prints the **A** (IPv4) and **AAAA** (IPv6) records you need to add at Network Solutions. Apex domains can't use CNAME — must be A + AAAA.

Optional — add the `www` subdomain too (recommended; most users type `www.`):

```bash
gcloud beta run domain-mappings create \
  --service=$SERVICE \
  --domain=www.$APEX \
  --region=$REGION \
  --project=$PROJECT
```

`www` mappings can use a CNAME (`www → ghs.googlehosted.com.`) at the registrar instead of A/AAAA — cleaner record set.

---

## Step 2 — Add the printed A/AAAA records at Network Solutions

Manual step at the registrar — Network Solutions → My Account → Domain Names → `opendriveclipboard.com` → Manage → Advanced DNS → A Records / AAAA Records section. Paste each record from Step 1's output. TTL default (3600).

Verify propagation:

```bash
dig +short A $APEX
dig +short AAAA $APEX
```

Expect 4 IPv4 addresses (216.239.32.21 / 34.21 / 36.21 / 38.21 typically) and 4 IPv6. Usually 5-30 min at Network Solutions.

---

## Step 3 — Confirm apex serves 200 with a managed cert

**Precondition:** Step 2 records resolve. After they resolve, Google auto-issues the TLS cert — usually 5-30 min, can take up to 24 h on first-time apex.

```bash
curl -s -o /dev/null -w "status=%{http_code}\nsize=%{size_download}\ncontent_type=%{content_type}\n" https://$APEX/
```

Expect `status=200`, `size=~4358`, `content_type=text/html; charset=utf-8`. If you see `status=000` or a TLS error, the cert is still provisioning — wait and retry. If you see `status=404`, the mapping didn't bind — `gcloud beta run domain-mappings describe --domain=$APEX --region=$REGION --project=$PROJECT` will show the resource conditions.

Sanity-check the API too:

```bash
curl -s https://$APEX/api/health
```

Expect `{"ok": true, "service": "opendrive-clipboard-demo"}`.

---

## Step 4 — Update the LMS env var

**Precondition:** Step 3 returned `status=200`.

In Laravel Cloud's dashboard for `streetlawopendrive.com`, set:

```
CLIPBOARD_DEMO_URL=https://opendriveclipboard.com
```

Redeploy (or wait for the next deploy). Verify the button on the LMS now points at the apex:

```bash
curl -s https://streetlawopendrive.com/clipboard | grep -oE 'href="https://[^"]+"' | head -3
```

Expect the apex URL in the output.

---

## Step 5 — Delete the orphaned `clipboard.streetlawopendrive.com` mapping

**Precondition:** Step 4 verified — the LMS button points at the apex, the apex serves 200. This is destructive (deletes the previous mapping). Confirm twice before running.

```bash
gcloud beta run domain-mappings delete \
  --domain=$ORPHAN \
  --region=$REGION \
  --project=$PROJECT \
  --quiet
```

Confirm:

```bash
gcloud beta run domain-mappings list --region=$REGION --project=$PROJECT
```

Should list only `opendriveclipboard.com` (and `www.opendriveclipboard.com` if you mapped it).

---

## Rollback

If the apex breaks after Step 5 and you need to point the LMS back at the auto-assigned URL:

```bash
# In Laravel Cloud env:
CLIPBOARD_DEMO_URL=https://opendrive-clipboard-demo-1010983542319.us-central1.run.app
```

The `*.run.app` URL is permanently assigned by Cloud Run and survives domain-mapping changes — it cannot be revoked while the service exists.
