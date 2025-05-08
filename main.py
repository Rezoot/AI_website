from flask import Flask, request, render_template, session, redirect, url_for
from ollama import chat, ChatResponse  # Import funkcji do komunikacji z modelem językowym

# Inicjalizacja aplikacji Flask
app = Flask(__name__)
app.secret_key = "tajny_klucz"  # Klucz sesji (potrzebny do działania cookies)

# Ustawienia
CHAR_LIMIT = 200  # Maksymalna długość wiadomości
# MAX_HISTORY = 10  # Opcjonalnie: limit wiadomości w historii

# Główna trasa widoku czatu
@app.route("/", methods=["GET", "POST"])
def chat_view():
    # Inicjalizacja historii wiadomości w sesji, jeśli nie istnieje
    if "messages" not in session:
        session["messages"] = []
        session["show"] = []


    error = None  # Zmienna do przechowywania ewentualnego błędu

    if request.method == "POST":
        # Pobierz wiadomość użytkownika z formularza
        user_msg = request.form.get("message", "").strip()

        # Walidacja wiadomości
        if len(user_msg) == 0:
            error = "Wiadomość nie może być pusta."
        elif len(user_msg) > CHAR_LIMIT:
            error = f"Twoja wiadomość jest za długa (limit {CHAR_LIMIT} znaków)."
        else:
            # Dodaj wiadomość użytkownika do historii
            session["messages"].append({"role": "user", "content": user_msg})
            session["show"].append({"role": "user", "content": user_msg})

            # (Opcjonalnie) ogranicz długość historii
            # session["messages"] = session["messages"][-MAX_HISTORY:]

            # Wygeneruj odpowiedź od modelu AI, używając historii
            response: ChatResponse = chat(
                model="deepseek-r1:8b",  # Nazwa modelu AI
                messages=session["messages"]
            )
            bot_reply = response.message.content  # Treść odpowiedzi od bota

            # Dodaj odpowiedź bota do historii
            session["messages"].append({"role": "assistant", "content": bot_reply})
            session["show"].append({"role": "assistant", "content": bot_reply[bot_reply.find('</think>')+8:]})
            session.modified = True  # Zaznacz, że sesja została zmieniona


            #print(session)  # Debug: wypisanie sesji w konsoli

            # Przekierowanie w celu uniknięcia ponownego przesłania formularza
            return redirect(url_for("chat_view"))

    # Wyświetlenie szablonu HTML z wiadomościami i ewentualnym błędem
    return render_template(
        "index.html",
        messages=session.get("show", []),
        error=error,
        char_limit=CHAR_LIMIT
    )

# Uruchomienie aplikacji w trybie debugowania
if __name__ == "__main__":
    app.run(debug=True)
