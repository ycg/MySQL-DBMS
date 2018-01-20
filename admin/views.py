from flask_admin import BaseView, expose


class MyView(BaseView):
    @expose("/")
    def index(self):
        return self.render("test_admin.html")
