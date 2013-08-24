import webapp2
import os
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), auto_reload = True)

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
	
def initForTest():
# jury rigged to add new student to db
		# 1. build the Course, which has name, description, importance
		course = Course(key_name = "222", parent = site_key(),
		name = "CECS TEST", description = "Long desc of course", importance = 50)
		course.put()
		key_to_course = db.Key.from_path('Course', "222", parent = site_key())
                # 2. build StudentCourse, which has Course and Rating
		new_student_course = StudentCourse(key_name = "test_sc", parent = site_key(),
		course = key_to_course, rating = 50)
		new_student_course.put()
		key_to_nsc = db.Key.from_path('StudentCourse', 'test_sc', parent = site_key())
                # 3. Build Student, which has username and student_courses (List of keys to SCs)
		new_student_courses_list = [key_to_nsc]
		new_student = Student(key_name = "tktran", parent = site_key(),
		username = "Tan Tran", student_courses = new_student_courses_list)
		new_student.put()

                # success!
                
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
		
		# initForTest()
		self.render('resume.html', courses = courses, skills = skills, languages = languages)

	def post(self):
		courses = self.request.get('courses-text')
		skills = self.request.get('skills-post')
		languages = self.request.get('languages-post')
		
	## ALL CODE FOR COURSES
		# For each course entered, check if it's valid.
		# If valid, enter into user
		courses_added = []
		courses_not_added = []
		
		# Get the current student
		student_key = db.Key.from_path('Student', "tktran", parent = site_key())
		student = db.get(student_key)
		# Get his courses
		courses_list = student.student_courses
		
		# For each course, see if it's allowed. If so, append to arrays for message
		for course in courses.split(','):
			key = db.Key.from_path('Course', course, parent=site_key())
			allowed_course = db.get(key)
			
			if allowed_course:
				courses_added.append(course)
				courses_list.append(key)
			else:
				courses_not_added.append(course)
		
		# Add the courses to the student
		student.student_courses = courses_list
		student.put()
		message = "These courses were added: " + ', '.join(courses_added)
		
		query = ""
		for course in courses_added:
			query = query + 'added='+course+"&"
		for course in courses_not_added:
			query = query + 'nadded='+course+"&"

		self.redirect('/success?' + query)

class SuccessPage(webapp2.RequestHandler):
	def write(self, *a, **kw):
		self.response.out.write(*a, **kw)

	def render_str(self, template, **params):
		return render_str(template, **params)

	def render(self, template, **kw):
		self.write(self.render_str(template, **kw))
			
	def get(self):
		query = self.request.GET
		added, nadded = query.getall('added'), query.getall('nadded')
		added, nadded = ', '.join(added), ', '.join(nadded)
		text = 'These courses were added: ' + added + '<br>' + \
			'These courses were not added: ' + nadded
		self.render('success.html', text = text)

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

class StudentCourse(db.Model):
	course = db.ReferenceProperty(Course)
	rating = db.RatingProperty(required = False)
	
class Student(db.Model):
	username = db.StringProperty(required = True)
	student_courses = db.ListProperty(db.Key)
	
	# back when I thought these were going to be csv
	# courses = db.StringProperty(required = False)
	# skills = db.StringProperty(required = False)
	# languages = db.StringProperty(required = False)
	
application = webapp2.WSGIApplication([ ('/', MainPage),
					('/resume', ResumePage),
					('/success', SuccessPage)], debug=True)
