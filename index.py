import webapp2
import os
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir))

def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)

class MainPage(webapp2.RequestHandler):
	def get(self):
		self.response.headers['Content-Type'] = 'text/html'
		template = jinja_env.get_template('index.html')
		
		template_values = {
			'username': 'First user'
		}

		self.response.write(template.render(template_values))

def site_key(name = 'default'):
	return db.Key.from_path('site', name)
	
class ResumePage(webapp2.RequestHandler):
	def write(self, *a, **kw):
		self.response.out.write(*a, **kw)

	def render_str(self, template, **params):
		return render_str(template, **params)

	def render(self, template, **kw):
		self.write(self.render_str(template, **kw))
			
	def get(self):
		courses = db.GqlQuery("select * from Course order by importance desc")
		skills = db.GqlQuery("select * from Skill")
		languages = db.GqlQuery("select * from Language")
		
		self.render('resume.html', courses = courses, skills = skills, languages = languages)

	def post(self):
		courses = self.request.get('courses-text')
##		courses_split = courses.split(',')
##		
##		course_numbers = []
##		for course in courses_split:
##			course_number = int(course)
##			course_numbers.append(course_number)
		
		for course in courses.split(','):
			key = db.Key.from_path('Course', course, parent=site_key())
			allowed_course = db.get(key)
			
			if not allowed_course:
				self.error(404)
				return
			
		new_course = Course(key_name = "222", parent = site_key(), 
			name = 'TestCourse2', description = 'Desc. of test', importance = 3)
		new_course.put()
		
		new_student = Student(username = "Tan Tran", parent = site_key())
		new_student.put()
		self.redirect('/success')

class SuccessPage(webapp2.RequestHandler):
	def write(self, *a, **kw):
		self.response.out.write(*a, **kw)

	def render_str(self, template, **params):
		return render_str(template, **params)

	def render(self, template, **kw):
		self.write(self.render_str(template, **kw))
			
	def get(self):
		self.render('success.html', message = 'These courses were added:')

class Course(db.Model):
	name = db.StringProperty(required = True)
	description = db.TextProperty(required = True)
	importance = db.RatingProperty(required = False)

	def render(self):
		return render_str("course.html", courseToDisplay = self)

class Skill(db.Model):
	name = db.StringProperty(required = True)
	description = db.TextProperty(required = True)
	
	def render(self):
		return render_str("skill.html", skillToDisplay = self)

class Language(db.Model):
	name = db.StringProperty(required = True)
	description = db.TextProperty(required = True)
	
	def render(self):
		return render_str("language.html", languageToDisplay = self)

class Student(db.Model):
	username = db.StringProperty(required = True)
	courses = db.StringProperty(required = False)
	skills = db.StringProperty(required = False)
	languages = db.StringProperty(required = False)
	
application = webapp2.WSGIApplication([ ('/', MainPage),
					('/resume', ResumePage),
					('/success', SuccessPage)], debug=True)
