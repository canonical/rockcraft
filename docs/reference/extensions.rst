Extensions
**********

Just as the Snapcraft extensions are designed to simplify Snap creation,
Rockcraft extensions are crafted to expand and modify the user-provided
rockcraft project file, aiming to minimise the boilerplate code when
initiating a new rock.

The ``flask-framework`` extension
---------------------------------

The Flask extension streamlines the process of building Flask application rocks.

It facilitates the installation of Flask application dependencies, including
Gunicorn, in the rock image. Additionally, it transfers your project files to
``/flask/app`` within the rock image.
