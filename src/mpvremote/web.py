import threading
from subprocess import PIPE, Popen

from flask import Flask, render_template, send_from_directory

from . import metadata, mpv


def launch_mpv(*args):
    print('Launching mpv with args:', *args)
    Popen(['mpv', *args], stdout=PIPE, stderr=PIPE).communicate()


def play_video(fname):
    try:
        fname = fname.replace('"', r'\"')
        mpv.send_mpv_command(f'raw loadfile "{fname}"')
    except ConnectionRefusedError:
        args = (fname, '--fullscreen')
        threading.Thread(target=launch_mpv, args=args).start()


def create_app():

    app = Flask(__name__)

    movies = metadata.retrieve_metadata(offline=True)

    def send_mpv_command(command):
        try:
            mpv.send_mpv_command(command)
        except ConnectionRefusedError:
            print('mpv socket connection refused')

    @app.route('/')
    def index():
        return render_template('index.html',
                               movies=enumerate(list(movies.values())))

    @app.route('/posters/<path:path>')
    def get_poster(path):
        return send_from_directory(metadata.POSTER_DIR, path)

    @app.route('/thumbnail_clicked/<int:thumbnail_index>')
    def thumbnail_clicked(thumbnail_index):
        movie = list(movies.values())[thumbnail_index]
        print(f"Playing movie: {movie['title']} ({movie['year']})")
        play_video(movie['path'])
        return 'Action performed'

    @app.route('/refresh')
    def refresh_database():
        global movies
        movies = metadata.retrieve_metadata(warn_dupes=False)
        return 'Refreshing local movie database'

    @app.route('/resume')
    def resume():
        send_mpv_command('set pause no')
        return 'Resumed'

    @app.route('/pause')
    def pause():
        send_mpv_command('set pause yes')
        return 'Paused'

    @app.route('/stop')
    def stop():
        send_mpv_command('quit')
        return 'Stopped'

    @app.route('/restart')
    def restart():
        send_mpv_command('seek 0 absolute')
        return 'Restarted'

    return app


def serve_prod():
    from subprocess import run
    run(['gunicorn', 'mpvremote.wsgi:app'])


def serve_debug():
    try:
        create_app().run(debug=True, host='0.0.0.0')
    except metadata.ApiException as exc:
        print(exc)
