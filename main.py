from flask import Flask, render_template, request, redirect, url_for, flash, session
from config import Config
from models import db, Candidate, Token, Vote
from datetime import datetime

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)

    # Middleware: cegah cache browser
    @app.after_request
    def add_header(response):
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '-1'
        return response

    @app.route("/hasil")
    def hasil():
        results = db.session.query(
            Candidate.nama,
            db.func.count(Vote.id).label("total_suara")
        ).outerjoin(Vote, Candidate.id == Vote.candidate_id) \
         .group_by(Candidate.id) \
         .order_by(db.func.count(Vote.id).desc()) \
         .all()
    
        # ubah hasil query jadi dictionary
        hasil_dict = {r.nama: r.total_suara for r in results}
    
        return render_template("hasil.html", hasil=hasil_dict)


    # === ROUTES ===
    @app.route("/", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            token_input = request.form.get("token")
            token = Token.query.filter_by(token=token_input).first()

            if not token:
                flash("Token tidak valid!", "danger")
                return redirect(url_for("login"))

            if token.status:
                flash("Token sudah digunakan!", "danger")
                return redirect(url_for("login"))

            session["token_id"] = token.id
            return redirect(url_for("candidates"))

        return render_template("login.html")

    @app.route("/candidates", methods=["GET", "POST"])
    def candidates():
        if "token_id" not in session:
            return redirect(url_for("login"))

        # Cek kalau token sudah dipakai, langsung lempar ke thankyou
        token = Token.query.get(session["token_id"])
        if token and token.status:
            return redirect(url_for("thankyou"))

        all_candidates = Candidate.query.all()

        if request.method == "POST":
            candidate_id = request.form.get("candidate_id")
            token_id = session["token_id"]

            # Simpan vote
            vote = Vote(token_id=token_id, candidate_id=candidate_id, waktu_vote=datetime.now())
            db.session.add(vote)

            # Update token
            token = Token.query.get(token_id)
            token.status = True
            token.waktu_pakai = datetime.now()

            db.session.commit()

            session.pop("token_id", None)  # hapus biar gak bisa vote lagi
            return redirect(url_for("thankyou"))

        return render_template("candidates.html", candidates=all_candidates)

    @app.route("/thankyou")
    def thankyou():
        return render_template("thankyou.html")

    @app.route("/api/hasil")
    def api_hasil():
        results = db.session.query(
            Candidate.nama,
            Candidate.kelas,
            db.func.count(Vote.id).label("total_suara")
        ).outerjoin(Vote, Candidate.id == Vote.candidate_id) \
         .group_by(Candidate.id) \
         .order_by(db.func.count(Vote.id).desc()) \
         .all()

        data = [
            {"nama": r.nama, "kelas": r.kelas, "total_suara": r.total_suara}
            for r in results
        ]
        return {"results": data}

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
