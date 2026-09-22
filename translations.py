"""UI translations for Corpus Analyzer.

Translations are looked up by key and rendered in the language stored in
``st.session_state.ui_language`` (``"en"`` or ``"de"``). If a key or language is
missing, the English fallback is returned.
"""

from typing import Dict

import streamlit as st

UI_TEXTS: Dict[str, Dict[str, str]] = {
    # Navigation / page titles
    "page_analyze": {"en": "Analyze", "de": "Analysieren"},
    "page_security": {"en": "Security", "de": "Sicherheit"},
    "page_feedback": {"en": "Feedback", "de": "Feedback"},
    "page_configuration": {"en": "Configuration", "de": "Einstellungen"},
    "page_about": {"en": "About", "de": "Über"},
    # Language selector
    "language_label": {"en": "Language", "de": "Sprache"},
    "language_english": {"en": "English", "de": "English"},
    "language_german": {"en": "Deutsch", "de": "Deutsch"},
    # Common actions
    "save": {"en": "Save", "de": "Speichern"},
    "send": {"en": "Send", "de": "Senden"},
    "cancel": {"en": "Cancel", "de": "Abbrechen"},
    "close": {"en": "Close", "de": "Schließen"},
    "remove": {"en": "Remove", "de": "Entfernen"},
    "download": {"en": "Download", "de": "Herunterladen"},
    "analyze": {"en": "Analyze", "de": "Analysieren"},
    "reanalyze": {"en": "Re-analyze", "de": "Neu analysieren"},
    "optional": {"en": "optional", "de": "optional"},
    # Page headers
    "analyze_title": {"en": "Analyze", "de": "Analysieren"},
    "analyze_subtitle": {
        "en": "Upload medical images, health photos, or photographed documents",
        "de": "Lade medizinische Bilder, Gesundheitsfotos oder fotografierte Dokumente hoch",
    },
    "security_title": {"en": "Security", "de": "Sicherheit"},
    "security_subtitle": {"en": "Security & Privacy", "de": "Sicherheit & Datenschutz"},
    "feedback_title": {"en": "Feedback", "de": "Feedback"},
    "feedback_subtitle": {"en": "Share your thoughts", "de": "Teile deine Meinung"},
    "configuration_title": {"en": "Configuration", "de": "Einstellungen"},
    "configuration_subtitle": {"en": "System settings", "de": "Systemeinstellungen"},
    "about_title": {"en": "About", "de": "Über"},
    "about_subtitle": {"en": "Corpus Analyzer", "de": "Corpus Analyzer"},
    # Sidebar
    "user_mode_label": {"en": "User mode", "de": "Nutzerrolle"},
    "view_results_as": {"en": "View results as", "de": "Ergebnisse anzeigen als"},
    "role_clinician": {"en": "Clinician", "de": "Arzt/Kliniker"},
    "role_patient": {"en": "Patient", "de": "Patient"},
    "role_researcher": {"en": "Researcher", "de": "Forscher"},
    "role_view": {"en": "view", "de": "Ansicht"},
    "response_language": {"en": "Response language", "de": "Antwortsprache"},
    # Sidebar info
    "sidebar_safety_privacy": {"en": "Safety & Privacy", "de": "Sicherheit & Datenschutz"},
    "sidebar_analysis_description": {
        "en": "This tool provides AI-powered analysis of medical images, health photos and photographed documents.",
        "de": "Dieses Tool bietet KI-gestützte Analyse von medizinischen Bildern, Gesundheitsfotos und fotografierten Dokumenten.",
    },
    "sidebar_disclaimer": {
        "en": "DISCLAIMER: This tool is for educational and informational purposes only. All analyses should be reviewed by qualified healthcare professionals. Do not make medical decisions based solely on this analysis.",
        "de": "HAFTUNGSAUSSCHLUSS: Dieses Tool dient ausschließlich Bildungs- und Informationszwecken. Alle Analysen sollten von qualifizierten Gesundheitsfachkräften überprüft werden. Treffen Sie keine medizinischen Entscheidungen allein aufgrund dieser Analyse.",
    },
    "sidebar_dicom_note": {
        "en": "DICOM files are anonymized locally (common identifying tags cleared) before analysis. This does not remove burned-in annotations in pixel data.",
        "de": "DICOM-Dateien werden vor der Analyse lokal anonymisiert (häufige identifizierende Tags werden entfernt). Eingebrannte Annotationen in den Bilddaten werden dadurch nicht entfernt.",
    },
    # Workflow / empty state
    "empty_state_title": {
        "en": "Upload or capture images to begin",
        "de": "Lade Bilder hoch oder mache Fotos, um zu starten",
    },
    "empty_state_description": {
        "en": "Corpus Analyzer uses AI to provide educational explanations of medical images, smartphone health photos, and photographed documents.",
        "de": "Corpus Analyzer nutzt KI, um medizinische Bilder, Smartphone-Gesundheitsfotos und fotografierte Dokumente verständlich zu erklären.",
    },
    "workflow_step1": {"en": "Upload image", "de": "Bild hochladen"},
    "workflow_step2": {"en": "Confirm privacy", "de": "Datenschutz bestätigen"},
    "workflow_step3": {"en": "Get analysis", "de": "Analyse erhalten"},
    # Upload / camera
    "tab_upload": {"en": "Upload files", "de": "Dateien hochladen"},
    "tab_camera": {"en": "Take photos", "de": "Fotos aufnehmen"},
    "upload_label": {"en": "Upload image(s)", "de": "Bild(er) hochladen"},
    "upload_help": {
        "en": "Supported formats: JPG, JPEG, PNG, DICOM, DCM. You can upload several files.",
        "de": "Unterstützte Formate: JPG, JPEG, PNG, DICOM, DCM. Mehrere Dateien sind möglich.",
    },
    "camera_label": {"en": "Take a photo", "de": "Foto aufnehmen"},
    "add_photo_button": {
        "en": "Add this photo to gallery",
        "de": "Dieses Foto zur Galerie hinzufügen",
    },
    "selected_images": {"en": "Selected images", "de": "Ausgewählte Bilder"},
    "camera_capture": {"en": "Camera capture", "de": "Kameraaufnahme"},
    "uploaded_image": {"en": "Uploaded image", "de": "Hochgeladenes Bild"},
    "image_details": {"en": "Image details", "de": "Bilddetails"},
    "format": {"en": "Format", "de": "Format"},
    "dimensions": {"en": "Dimensions", "de": "Abmessungen"},
    "dicom_anonymized_note": {
        "en": "DICOM metadata was anonymized locally before conversion.",
        "de": "DICOM-Metadaten wurden vor der Konvertierung lokal anonymisiert.",
    },
    # Photo guidance
    "photo_tips": {
        "en": "**Photo tips:** Use good, even lighting. Keep the camera steady and in focus. Include a coin or ruler as a scale if possible. Take one close-up and one overview photo. Use a plain, neutral background.",
        "de": "**Foto-Tipps:** Nutze gleichmäßiges, gutes Licht. Halte die Kamera ruhig und scharf. Füge wenn möglich eine Münze oder ein Lineal als Maßstab hinzu. Mache eine Nahaufnahme und eine Übersicht. Verwende einen neutralen Hintergrund.",
    },
    # Privacy options
    "privacy_strip_exif": {
        "en": "Remove EXIF/GPS metadata from photos before analysis",
        "de": "EXIF/GPS-Metadaten aus Fotos vor der Analyse entfernen",
    },
    "privacy_blur_faces": {
        "en": "Blur faces and tattoos (experimental, local processing; requires opencv-python)",
        "de": "Gesichter und Tattoos verwischen (experimentell, lokale Verarbeitung; erfordert opencv-python)",
    },
    "privacy_blur_unavailable": {
        "en": "Install opencv-python to enable face/tattoo blurring.",
        "de": "Installiere opencv-python, um Gesichter-/Tattoo-Verwischung zu aktivieren.",
    },
    # Consent
    "consent_title": {
        "en": "Privacy confirmation required",
        "de": "Datenschutzbestätigung erforderlich",
    },
    "consent_intro": {
        "en": "Before analysis, please confirm:",
        "de": "Bitte bestätige vor der Analyse:",
    },
    "consent_item_1": {
        "en": "The image bytes will be sent to the selected AI provider.",
        "de": "Die Bilddaten werden an den gewählten KI-Anbieter gesendet.",
    },
    "consent_item_2": {
        "en": "Your prompt text will be sent to the selected AI provider.",
        "de": "Dein Prompt-Text wird an den gewählten KI-Anbieter gesendet.",
    },
    "consent_item_3": {
        "en": "DICOM metadata is anonymized locally and is not sent.",
        "de": "DICOM-Metadaten werden lokal anonymisiert und nicht gesendet.",
    },
    "consent_item_4": {
        "en": "EXIF/GPS metadata is stripped from smartphone photos before sending.",
        "de": "EXIF/GPS-Metadaten werden aus Smartphone-Fotos vor dem Senden entfernt.",
    },
    "consent_item_5": {
        "en": "Burned-in text/annotations inside the image pixels may still be visible.",
        "de": "Eingebrannter Text oder Annotationen in den Bildpixeln können weiterhin sichtbar sein.",
    },
    "consent_why_title": {"en": "Why is this required?", "de": "Warum ist das erforderlich?"},
    "consent_why_text": {
        "en": "Medical images and health photos may contain protected health information. This confirmation helps ensure you do not accidentally send identifiable data to an external AI service.",
        "de": "Medizinische Bilder und Gesundheitsfotos können gesundheitsbezogene Daten enthalten. Diese Bestätigung stellt sicher, dass du keine identifizierbaren Daten versehentlich an einen externen KI-Dienst sendest.",
    },
    "consent_checkbox": {
        "en": "I confirm this upload and text contain no sensitive patient-identifying information",
        "de": "Ich bestätige, dass dieser Upload und Text keine sensiblen patientenbezogenen Daten enthalten",
    },
    # Anamnesis
    "anamnesis_title": {"en": "About this photo / Anamnese", "de": "Zum Foto / Anamnese"},
    "anamnesis_since_when": {"en": "Since when?", "de": "Seit wann?"},
    "anamnesis_changed": {"en": "Has it changed?", "de": "Hat es sich verändert?"},
    "anamnesis_size": {"en": "Approximate size", "de": "Ungefähre Größe"},
    "anamnesis_itching": {"en": "Itching?", "de": "Juckreiz?"},
    "anamnesis_bleeding": {"en": "Bleeding?", "de": "Blutung?"},
    "anamnesis_pain": {"en": "Pain?", "de": "Schmerzen?"},
    "anamnesis_notes": {"en": "Additional notes", "de": "Weitere Hinweise"},
    "anamnesis_label": {"en": "Anamnesis", "de": "Anamnese"},
    # Quick prompts
    "quick_prompts_label": {
        "en": "Quick prompts (select one or more)",
        "de": "Schnell-Prompts (eine oder mehrere auswählen)",
    },
    "quick_prompt_radiology": {"en": "Radiology-style report", "de": "Radiologie-Report"},
    "quick_prompt_patient": {"en": "Explain for patient", "de": "Für Patienten erklären"},
    "quick_prompt_redflags": {"en": "Focus: red flags", "de": "Fokus: Warnzeichen"},
    "quick_prompt_research": {"en": "Online research", "de": "Online-Recherche"},
    "quick_prompt_context": {"en": "Add patient context", "de": "Patientenkontext hinzufügen"},
    "additional_context_label": {
        "en": "Additional context (e.g., patient history, symptoms)",
        "de": "Zusätzlicher Kontext (z. B. Krankengeschichte, Symptome)",
    },
    "additional_context_placeholder": {
        "en": "Enter any relevant information here...",
        "de": "Gib hier relevante Informationen ein...",
    },
    # Analysis spinner / errors
    "analysis_spinner": {"en": "Analyzing... Please wait.", "de": "Analysiere... Bitte warten."},
    "consent_missing_error": {
        "en": "Please confirm the privacy statement before analyzing.",
        "de": "Bitte bestätige die Datenschutzerklärung vor der Analyse.",
    },
    "analysis_error": {
        "en": "Sorry, we could not analyze the image(s). Please try again or contact support.",
        "de": "Leider konnten wir das/die Bild(er) nicht analysieren. Bitte versuche es erneut oder kontaktiere den Support.",
    },
    "api_key_error": {
        "en": "If the problem persists, check that your OpenAI API key is valid and has access to the selected model.",
        "de": "Wenn das Problem weiterhin besteht, prüfe, ob dein OpenAI-API-Key gültig ist und Zugriff auf das gewählte Modell hat.",
    },
    "no_results_for_role": {
        "en": "No analysis results available for this role yet.",
        "de": "Für diese Rolle liegen noch keine Analyseergebnisse vor.",
    },
    "role_switch_info": {
        "en": "Switching to **{role}** mode requires a new analysis tailored for that audience.",
        "de": "Der Wechsel in den Modus **{role}** erfordert eine neue Analyse für diese Zielgruppe.",
    },
    "reanalyze_as": {"en": "Re-analyze as {role}", "de": "Neu analysieren als {role}"},
    # Analysis results
    "analysis_results_title": {"en": "Analysis Results", "de": "Analyseergebnisse"},
    "confidence_label": {"en": "Confidence", "de": "Konfidenz"},
    "clinical_details": {"en": "Clinical details", "de": "Klinische Details"},
    "patient_education": {"en": "Patient Education", "de": "Aufklärung für Patienten"},
    "full_analysis": {"en": "Full analysis", "de": "Vollständige Analyse"},
    "raw_analysis": {"en": "Raw analysis", "de": "Roh-Analyse"},
    "raw_response": {"en": "Raw response", "de": "Roh-Antwort"},
    "ai_review_note": {
        "en": "Note: This analysis is generated by AI and should be reviewed by a qualified healthcare professional.",
        "de": "Hinweis: Diese Analyse wurde von einer KI erstellt und sollte von einer qualifizierten Gesundheitsfachkraft überprüft werden.",
    },
    # Report actions
    "report_actions_title": {"en": "Report actions", "de": "Berichtsaktionen"},
    "download_markdown": {"en": "Download Markdown", "de": "Markdown herunterladen"},
    "download_pdf": {"en": "Download PDF", "de": "PDF herunterladen"},
    "pdf_disabled": {"en": "PDF export disabled", "de": "PDF-Export deaktiviert"},
    # Security page
    "security_how_data_handled": {
        "en": "How your data is handled",
        "de": "Wie deine Daten verarbeitet werden",
    },
    "security_upload_title": {"en": "Upload", "de": "Upload"},
    "security_upload_text": {
        "en": "Uploaded images (JPG/PNG), DICOM files, and photographed documents are received via Streamlit's file uploader and kept in memory for the current session only. By default, nothing is written to disk or stored between sessions.",
        "de": "Hochgeladene Bilder (JPG/PNG), DICOM-Dateien und fotografierte Dokumente werden über Streamlits Datei-Upload empfangen und nur für die aktuelle Sitzung im Arbeitsspeicher gehalten. Standardmäßig wird nichts auf die Festplatte geschrieben oder zwischen Sitzungen gespeichert.",
    },
    "security_dicom_title": {"en": "DICOM anonymization", "de": "DICOM-Anonymisierung"},
    "security_dicom_text": {
        "en": "If you upload a DICOM file (.dcm/.dicom), common identifying metadata tags are cleared locally before analysis. Burned-in annotations or text embedded in the image pixels are not removed.",
        "de": "Wenn du eine DICOM-Datei (.dcm/.dicom) hochlädst, werden häufige identifizierende Metadaten-Tags vor der Analyse lokal entfernt. Eingebrannte Annotationen oder im Bild eingebetteter Text werden nicht entfernt.",
    },
    "security_photo_title": {"en": "Photo privacy", "de": "Foto-Datenschutz"},
    "security_photo_text": {
        "en": "Smartphone photos can contain EXIF metadata including GPS coordinates. Before analysis, EXIF/GPS data is stripped locally. Optional face/tattoo masking is available as an experimental, disabled-by-default feature.",
        "de": "Smartphone-Fotos können EXIF-Metadaten einschließlich GPS-Koordinaten enthalten. Vor der Analyse werden EXIF/GPS-Daten lokal entfernt. Die optionale Gesichts-/Tattoo-Maskierung ist ein experimentelles, standardmäßig deaktiviertes Feature.",
    },
    "security_sent_title": {"en": "What is sent", "de": "Was gesendet wird"},
    "security_sent_text": {
        "en": "Only your prompt text and the image/document bytes are sent to the configured AI provider (e.g., OpenAI) to generate an analysis.",
        "de": "Nur dein Prompt-Text und die Bild-/Dokument-Bytes werden an den konfigurierten KI-Anbieter (z. B. OpenAI) gesendet, um eine Analyse zu erzeugen.",
    },
    "security_not_stored_title": {"en": "What is not stored", "de": "Was nicht gespeichert wird"},
    "security_not_stored_text": {
        "en": "The app does not write uploaded images to disk as part of analysis. Sessions are temporary. Progress tracking over time is planned as a strictly opt-in, encrypted, deletable feature and is not active in this release.",
        "de": "Die App schreibt hochgeladene Bilder nicht als Teil der Analyse auf die Festplatte. Sitzungen sind temporär. Die langfristige Verlaufsverfolgung ist als strikt opt-in, verschlüsseltes, löschbares Feature geplant und in diesem Release nicht aktiv.",
    },
    "security_law_title": {"en": "Data protection law", "de": "Datenschutzrecht"},
    "security_law_text": {
        "en": "Health data is special-category data under GDPR Art. 9. Corpus Analyzer is designed for de-identified, educational use. HIPAA considerations apply for US contexts. Before any progress-tracking or triage-related features are released, the legal basis, processor agreements, and any cross-border data transfers must be clarified.",
        "de": "Gesundheitsdaten sind nach DSGVO Art. 9 besondere Kategorien personenbezogener Daten. Corpus Analyzer ist für anonymisierte, bildungsorientierte Nutzung konzipiert. Für US-Kontexte gelten HIPAA-Erwägungen. Bevor Funktionen zur Verlaufsverfolgung oder Triage veröffentlicht werden, müssen Rechtsgrundlage, Auftragsverarbeitungsverträge und grenzüberschreitende Datenübertragungen geklärt werden.",
    },
    "security_retention_title": {
        "en": "Data retention at the AI provider",
        "de": "Datenspeicherung beim KI-Anbieter",
    },
    "security_retention_text": {
        "en": "We use OpenAI models via the OpenAI API. OpenAI states that API inputs/outputs are not used to train OpenAI models by default, and we do not explicitly opt in. OpenAI retains certain request/response data for abuse monitoring and safety purposes for 30 days, after which it is deleted. Always verify the current policy at the link below.",
        "de": "Wir verwenden OpenAI-Modelle über die OpenAI-API. OpenAI gibt an, dass API-Eingaben/-Ausgaben standardmäßig nicht zum Trainieren von OpenAI-Modellen verwendet werden, und wir stimmen nicht explizit zu. OpenAI bewahrt bestimmte Anfrage-/Antwortdaten zur Missbrauchserkennung und Sicherheit 30 Tage auf, danach werden sie gelöscht. Bitte prüfe die aktuelle Richtlinie über den unten stehenden Link.",
    },
    "security_openai_button": {
        "en": "OpenAI: How your data is used",
        "de": "OpenAI: Wie deine Daten verwendet werden",
    },
    "security_contact": {"en": "Contact", "de": "Kontakt"},
    "security_contact_text": {
        "en": "Questions or vulnerability reports? Contact us at **{email}**.",
        "de": "Fragen oder Sicherheitsmeldungen? Kontaktiere uns unter **{email}**.",
    },
    # About page
    "about_what_does": {"en": "What Corpus Analyzer does", "de": "Was Corpus Analyzer macht"},
    "about_what_does_text": {
        "en": "Corpus Analyzer is an educational tool that helps you understand what your images and documents show. Upload an X-ray, MRI, CT, ultrasound, or DICOM image; a smartphone photo of a mole, nail, rash, or wound; or a photographed doctor's letter, lab report, or medication package. You will receive a structured, AI-generated report tailored to your role — patient, clinician, or researcher.",
        "de": "Corpus Analyzer ist ein Bildungs-Tool, das dir hilft zu verstehen, was deine Bilder und Dokumente zeigen. Lade ein Röntgen-, MRT-, CT-, Ultraschall- oder DICOM-Bild hoch; ein Smartphone-Foto eines Leberflecks, Nagels, Ausschlags oder einer Wunde; oder einen fotografierten Arztbrief, Laborbefund oder Medikamentenpackung. Du erhältst einen strukturierten, KI-generierten Bericht, angepasst an deine Rolle — Patient, Arzt/Kliniker oder Forscher.",
    },
    "about_how_to_use": {"en": "How to use it", "de": "So wird es genutzt"},
    "about_step1": {
        "en": "Go to **Analyze** and upload or capture one or more images or documents.",
        "de": "Gehe zu **Analysieren** und lade ein oder mehrere Bilder oder Dokumente hoch oder mache Fotos.",
    },
    "about_step2": {
        "en": "Confirm that the images contain no patient-identifying information.",
        "de": "Bestätige, dass die Bilder keine patientenidentifizierenden Informationen enthalten.",
    },
    "about_step3": {
        "en": "Choose the response **language** (English or Deutsch) in the sidebar.",
        "de": "Wähle die **Sprache** der Antwort (English oder Deutsch) in der Seitenleiste.",
    },
    "about_step4": {
        "en": "Select one or more **quick prompts** (e.g., radiology style, red flags, online research) or type your own context.",
        "de": "Wähle einen oder mehrere **Schnell-Prompts** (z. B. Radiologie-Report, Warnzeichen, Online-Recherche) oder gib deinen eigenen Kontext ein.",
    },
    "about_step5": {
        "en": "Optionally fill in the **anamnesis** questions to give the model more context.",
        "de": "Fülle optional die **Anamnese**-Fragen aus, um dem Modell mehr Kontext zu geben.",
    },
    "about_step6": {
        "en": "Click **Analyze** and wait for the structured report.",
        "de": "Klicke auf **Analysieren** und warte auf den strukturierten Bericht.",
    },
    "about_step7": {
        "en": "Switch between **Clinician**, **Patient** and **Researcher** views. Each mode generates a report tailored for that audience; switching modes after an analysis offers a **Re-analyze** button for the new role.",
        "de": "Wechsle zwischen den Ansichten **Arzt/Kliniker**, **Patient** und **Forscher**. Jeder Modus erzeugt einen für diese Zielgruppe angepassten Bericht; nach einer Analyse bietet der Wechsel einen Button **Neu analysieren** für die neue Rolle.",
    },
    "about_step8": {
        "en": "Download the report as Markdown or PDF.",
        "de": "Lade den Bericht als Markdown oder PDF herunter.",
    },
    "about_research": {"en": "Research & references", "de": "Recherche & Quellen"},
    "about_research_text": {
        "en": "The **Online research** quick prompt asks the model to include current authoritative references (for example PubMed, medical society guidelines, or clinical journal articles) and cite them with URLs. Corpus Analyzer uses a local web-fetcher tool for live page retrieval.",
        "de": "Der Schnell-Prompt **Online-Recherche** weist das Modell an, aktuelle autoritative Quellen (z. B. PubMed, Leitlinien medizinischer Fachgesellschaften oder klinische Fachzeitschriften) einzubeziehen und mit URLs zu zitieren. Corpus Analyzer nutzt dazu ein lokales Web-Fetcher-Tool zum Abrufen von Seiten.",
    },
    "about_important": {"en": "Important", "de": "Wichtig"},
    "about_important_warning": {
        "en": "This tool is for educational and orientation purposes only. It is not CE-marked or FDA-cleared for clinical decision-making. All analyses should be reviewed by qualified healthcare professionals. Always consult a qualified healthcare provider for medical advice, diagnosis, or treatment.",
        "de": "Dieses Tool dient ausschließlich Bildungs- und Orientierungszwecken. Es ist nicht als Medizinprodukt CE-kennzeichnet oder von der FDA für klinische Entscheidungsfindung zugelassen. Alle Analysen sollten von qualifizierten Gesundheitsfachkräften überprüft werden. Ziehe immer einen qualifizierten Gesundheitsdienstleister für medizinischen Rat, Diagnose oder Behandlung hinzu.",
    },
    "about_resources": {"en": "Resources", "de": "Ressourcen"},
    "about_report_issue": {"en": "Report an issue", "de": "Problem melden"},
    "about_request_feature": {"en": "Request a feature", "de": "Feature wünschen"},
    "about_security_privacy": {"en": "Security & Privacy", "de": "Sicherheit & Datenschutz"},
    # Feedback page
    "feedback_report_title": {
        "en": "Report bugs / request features",
        "de": "Fehler melden / Features wünschen",
    },
    "feedback_bug_report": {"en": "Bug report", "de": "Fehlerbericht"},
    "feedback_feature_request": {"en": "Feature request", "de": "Feature-Wunsch"},
    "feedback_no_repo": {
        "en": "GitHub links are not configured. Set the environment variable ``GITHUB_REPO_URL`` (e.g. https://github.com/<org>/<repo>) to enable one-click issue links.",
        "de": "GitHub-Links sind nicht konfiguriert. Setze die Umgebungsvariable ``GITHUB_REPO_URL`` (z. B. https://github.com/<org>/<repo>), um Ein-Klick-Issue-Links zu aktivieren.",
    },
    "feedback_rate_title": {"en": "Rate the app", "de": "App bewerten"},
    "feedback_text_label": {"en": "Your feedback", "de": "Dein Feedback"},
    "feedback_text_placeholder": {
        "en": "What worked well? What should be improved?",
        "de": "Was hat gut funktioniert? Was können wir verbessern?",
    },
    "feedback_name_label": {"en": "Name (optional)", "de": "Name (optional)"},
    "feedback_email_label": {"en": "Email address (optional)", "de": "E-Mail-Adresse (optional)"},
    "feedback_submit": {"en": "Send feedback", "de": "Feedback senden"},
    "feedback_missing": {
        "en": "Please enter some feedback before sending.",
        "de": "Bitte gib Feedback ein, bevor du es sendest.",
    },
    "feedback_send_error": {
        "en": "Could not send feedback email. Please check SMTP settings (SMTP_HOST, SMTP_PORT, SMTP_FROM, SMTP_TO, SMTP_USERNAME, SMTP_PASSWORD, SMTP_USE_TLS).",
        "de": "Feedback-E-Mail konnte nicht gesendet werden. Bitte prüfe die SMTP-Einstellungen (SMTP_HOST, SMTP_PORT, SMTP_FROM, SMTP_TO, SMTP_USERNAME, SMTP_PASSWORD, SMTP_USE_TLS).",
    },
    "feedback_thanks": {
        "en": "Thanks — your feedback was sent!",
        "de": "Danke — dein Feedback wurde gesendet!",
    },
    # Configuration page
    "config_model_section": {"en": "AI Model", "de": "KI-Modell"},
    "config_select_model": {"en": "Select a model", "de": "Modell auswählen"},
    "config_save_model": {"en": "Save Model Configuration", "de": "Modelleinstellung speichern"},
    "config_model_saved": {
        "en": "Default model set to {model}",
        "de": "Standardmodell auf {model} gesetzt",
    },
    "config_api_key_section": {"en": "API Key", "de": "API-Key"},
    "config_cloud_warning": {
        "en": "You're running this app online. Please enter your own API key below. This key will be stored in your session and won't be saved permanently.",
        "de": "Du führst die App online aus. Bitte gib unten deinen eigenen API-Key ein. Der Key wird in deiner Sitzung gespeichert und nicht dauerhaft gespeichert.",
    },
    "config_api_key_input": {
        "en": "Enter your OpenAI API Key",
        "de": "Gib deinen OpenAI-API-Key ein",
    },
    "config_api_key_help": {
        "en": "Your OpenAI API key for accessing GPT models",
        "de": "Dein OpenAI-API-Key für den Zugriff auf GPT-Modelle",
    },
    "config_api_key_applied": {
        "en": "API Key applied for this session!",
        "de": "API-Key für diese Sitzung übernommen!",
    },
    "config_api_key_missing": {
        "en": "Please enter your OpenAI API key to use this application.",
        "de": "Bitte gib deinen OpenAI-API-Key ein, um die App zu nutzen.",
    },
    "config_beta_active": {"en": "BETA mode active", "de": "BETA-Modus aktiv"},
    "config_beta_text": {
        "en": "No API key is required yet — this project is currently sponsored. If you want to use your own key, set ``OPENAI_API_KEY`` in your environment.",
        "de": "Derzeit ist noch kein API-Key erforderlich — dieses Projekt wird aktuell gesponsert. Wenn du deinen eigenen Key nutzen möchtest, setze ``OPENAI_API_KEY`` in deiner Umgebung.",
    },
    "config_web_fetcher_section": {"en": "Web Fetcher", "de": "Web-Fetcher"},
    "config_web_fetcher_enabled": {
        "en": "Web fetcher is enabled. The medical agent can retrieve web pages and literature.",
        "de": "Web-Fetcher ist aktiviert. Der Medizin-Agent kann Webseiten und Fachliteratur abrufen.",
    },
    "config_web_fetcher_disabled": {
        "en": "Web fetcher is disabled. Set ``ENABLE_WEB_FETCHER=true`` to enable it.",
        "de": "Web-Fetcher ist deaktiviert. Setze ``ENABLE_WEB_FETCHER=true``, um ihn zu aktivieren.",
    },
    # Footer
    "footer_made_with": {"en": "Made with", "de": "Gemacht mit"},
    "footer_by": {"en": "by", "de": "von"},
}


def get_language() -> str:
    """Return the active UI language from session state, defaulting to English."""
    return st.session_state.get("ui_language", "en")


def set_language(language: str) -> None:
    """Persist the selected UI language in Streamlit session state."""
    st.session_state["ui_language"] = language


def _(key: str) -> str:
    """Return the translated string for ``key`` in the active UI language.

    Falls back to English if the key or selected language is missing.
    """
    lang = get_language()
    return UI_TEXTS.get(key, {}).get(lang) or UI_TEXTS.get(key, {}).get("en", key)


def format_text(key: str, **kwargs) -> str:
    """Return the translated string with placeholder substitution."""
    return _(key).format(**kwargs)
