Extensions
**********

Just as the snapcraft extensions are designed to simplify snap creation,
Rockcraft extensions are crafted to expand and modify the user-provided
rockcraft manifest file, aiming to minimize the boilerplate code when
initiating a new rock.

The flask extension
-------------------

The Flask extension streamlines the process of building Flask application rocks.

It facilitates the installation of Flask application dependencies, including
Gunicorn, in the rock image. Additionally, it transfers your project files to
``/srv/flask/app`` within the rock image.
