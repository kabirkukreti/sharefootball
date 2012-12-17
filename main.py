import wsgiref.handlers

from google.appengine.ext import webapp
from app import views

application = webapp.WSGIApplication([
  ('/admin/match', views.AdminMatch),
  ('/admin', views.Admin),
  ('/sandbox', views.Sandbox),
  ('/classify', views.Classify),
  ('/match', views.Match),
  ('/piece', views.Piece),
  ('/appearance', views.Appearance),
  ('/userdetails', views.UserDetails),
  ('/delete', views.Delete),
  ('/', views.IndexHandler),
  ('/search', views.Search),
  ('/team', views.Team),
  ('/init/comments', views.InitComments),
  ('/init', views.Init),
  ('/init/funfacts', views.InitFunfacts),
  ('/clear', views.Clear),

], debug=True)

def main():
  wsgiref.handlers.CGIHandler().run(application)