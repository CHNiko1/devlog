"""
Error handlers for the DevLog app
These show nice error pages when something goes wrong
"""


def setup_error_handlers(app):
    """
    This function sets up all the error handlers
    Call this function in app.py to register all error handlers
    """
    
    @app.errorhandler(404)
    def not_found(error):
        """Show 404 page when user goes to a page that doesn't exist"""
        return render_template('404.html'), 404
    
    
    @app.errorhandler(500)
    def server_error(error):
        """Show 500 page when something goes wrong on the server"""
        return render_template('500.html'), 500


# Import render_template at the bottom to avoid issues
from flask import render_template
