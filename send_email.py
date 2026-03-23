import sqlite3
import os
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()
GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_PASSWORD = os.getenv("GMAIL_PASSWORD")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "db.sqlite3")


def get_subscribers():
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute("SELECT email FROM subscribers").fetchall()
    conn.close()
    return [r[0] for r in rows]


def send_email(to_email, subject, html):
    msg = MIMEText(html, "html")
    msg["Subject"] = subject
    msg["From"] = GMAIL_USER
    msg["To"] = to_email
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(GMAIL_USER, GMAIL_PASSWORD)
        server.sendmail(GMAIL_USER, to_email, msg.as_string())


def send_email_to_all(word):
    if not word:
        print("No word data passed!")
        return

    subscribers = get_subscribers()
    if not subscribers:
        print("No subscribers found.")
        return

    print(f"Sending email to {len(subscribers)} subscribers...")

    w           = word.get("word", "")
    phonetic    = word.get("phonetic", "") or ""
    pos         = word.get("part_of_speech", "") or ""
    meaning     = word.get("meaning", "") or "—"
    example     = word.get("example", "") or ""
    synonyms    = word.get("synonyms", "") or ""
    antonyms    = word.get("antonyms", "") or ""

    # Phonetic
    phonetic_block = f'<p style="font-family:Georgia,serif;font-style:italic;font-size:17px;color:#7EB3FF;margin:6px 0 0;">"{phonetic}"</p>' if phonetic else ""

    # Part of speech badge — matches webpage pill style
    pos_block = f'''
        <span style="display:inline-block;background:rgba(255,255,255,0.12);border:1px solid rgba(255,255,255,0.22);
        color:#CBD5E1;border-radius:100px;padding:3px 14px;font-size:11px;font-weight:600;
        letter-spacing:1.5px;text-transform:uppercase;margin-top:12px;">{pos}</span>
    ''' if pos else ""

    # Example block — matches blue left-border style on webpage
    example_block = f'''
        <table width="100%" cellpadding="0" cellspacing="0" style="margin:0 0 20px;">
          <tr>
            <td width="3" style="background:#2563EB;border-radius:2px;">&nbsp;</td>
            <td style="background:#EEF2FA;padding:12px 16px;border-radius:0 6px 6px 0;">
              <p style="margin:0;font-family:Georgia,serif;font-style:italic;color:#4B5563;font-size:15px;">"{example}"</p>
            </td>
          </tr>
        </table>
    ''' if example else ""

    # Synonym chips
    def build_chips(text, color, bg, border):
        if not text or not text.strip():
            return '<span style="color:#9CA3AF;font-style:italic;font-size:13px;">—</span>'
        chips = ""
        for w in text.split(","):
            w = w.strip()
            if w:
                chips += f'<span style="display:inline-block;background:{bg};color:{color};border:1px solid {border};border-radius:100px;padding:3px 12px;font-size:12px;font-weight:500;margin:3px 4px 3px 0;">{w}</span>'
        return chips

    syn_chips = build_chips(synonyms, "#2563EB", "#DBEAFE", "#BFDBFE")
    ant_chips = build_chips(antonyms, "#DC2626", "#FEE2E2", "#FECACA")

    for email in subscribers:
        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <body style="margin:0;padding:0;background-color:#F0F3FA;font-family:'DM Sans',Arial,sans-serif;">
        <table width="100%" cellpadding="0" cellspacing="0" style="background:#F0F3FA;padding:36px 16px;">
          <tr><td align="center">
            <table width="600" cellpadding="0" cellspacing="0" style="border-radius:12px;overflow:hidden;box-shadow:0 4px 24px rgba(14,30,61,0.10);">

              <!-- NAV BAR -->
              <tr>
                <td style="background:#0E1E3D;padding:0 36px;height:54px;">
                  <table width="100%" cellpadding="0" cellspacing="0">
                    <tr>
                      <td style="font-family:Georgia,serif;font-size:20px;color:#FFFFFF;">
                        Daily<em style="color:#7EB3FF;">Drop</em>
                      </td>
                      <td align="right" style="font-size:11px;color:#7EB3FF;letter-spacing:0.5px;font-weight:600;">
                        WORD OF THE DAY
                      </td>
                    </tr>
                  </table>
                </td>
              </tr>

              <!-- HERO — matches webpage navy gradient -->
              <tr>
                <td style="background:linear-gradient(135deg,#0E1E3D 0%,#16305E 60%,#1E4080 100%);padding:48px 36px 56px;text-align:center;">
                  <h1 style="font-family:Georgia,serif;font-size:58px;color:#FFFFFF;margin:0;line-height:1.0;">{w}</h1>
                  {phonetic_block}
                  {pos_block}
                </td>
              </tr>

              <!-- DETAIL CARD — matches white card on webpage -->
              <tr>
                <td style="background:#FFFFFF;padding:36px 36px 28px;">

                  <!-- Definition -->
                  <p style="font-size:10px;letter-spacing:2.5px;text-transform:uppercase;color:#2563EB;font-weight:700;margin:0 0 8px;">Definition</p>
                  <p style="font-size:16px;color:#111827;line-height:1.8;margin:0 0 24px;">{meaning}</p>

                  <!-- Example -->
                  {example_block}

                  <!-- Divider -->
                  <table width="100%" cellpadding="0" cellspacing="0" style="margin:4px 0 20px;">
                    <tr><td style="border-top:1px solid #C8D5EE;font-size:0;">&nbsp;</td></tr>
                  </table>

                  <!-- Synonyms & Antonyms side by side -->
                  <table width="100%" cellpadding="0" cellspacing="0">
                    <tr>
                      <td width="50%" valign="top" style="padding-right:16px;">
                        <p style="font-size:10px;letter-spacing:2.5px;text-transform:uppercase;color:#2563EB;font-weight:700;margin:0 0 10px;">Synonyms</p>
                        {syn_chips}
                      </td>
                      <td width="50%" valign="top">
                        <p style="font-size:10px;letter-spacing:2.5px;text-transform:uppercase;color:#2563EB;font-weight:700;margin:0 0 10px;">Antonyms</p>
                        {ant_chips}
                      </td>
                    </tr>
                  </table>

                </td>
              </tr>

              <!-- CTA -->
              <tr>
                <td style="background:#FFFFFF;padding:8px 36px 36px;text-align:center;">
                  <a href="https://dhyana.pythonanywhere.com/"
                     style="display:inline-block;background:#2563EB;color:#FFFFFF;text-decoration:none;
                     padding:13px 32px;border-radius:8px;font-size:14px;font-weight:600;letter-spacing:0.5px;">
                    View on DailyDrop →
                  </a>
                </td>
              </tr>

              <!-- FOOTER -->
              <tr>
                <td style="background:#F0F3FA;padding:20px 36px;text-align:center;border-top:1px solid #C8D5EE;">
                  <p style="margin:0;font-size:12px;color:#9CA3AF;">
                    You're receiving this because you subscribed to DailyDrop.<br>
                    <a href="https://dhyana.pythonanywhere.com/unsubscribe?email={email}"
                       style="color:#2563EB;text-decoration:none;">Unsubscribe</a>
                  </p>
                </td>
              </tr>

            </table>
          </td></tr>
        </table>
        </body>
        </html>
        """
        try:
            send_email(email, f"DailyDrop: {w}", html)
            print(f"  ✓ Sent to {email}")
        except Exception as e:
            print(f"  ✗ Failed to send to {email}: {e}")

    print("Done sending emails.")


if __name__ == "__main__":
    print("Run this via daily_job.py")