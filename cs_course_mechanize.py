#I DID NOT WRITE THIS CODE THE MAJORITY OF THIS CODE I JUST EDITED IT FOR MY USES.
#SEE http://www.ccs.neu.edu/course/cs3650/parent/ FOR ORIGINAL COPY OF CODE
#My mission here is to update this code and so that I can use it for my class sechedules
#In Addition I want to update this code so I can use it for other web-pages 
#Lastly, I want to clean this code the way it is written now is quite messy and code be much simpler

import sys
import os
import re
import mechanize
# import cookielib

# Modify these global variables:
URL = "https://wl11gp.neu.edu/udcprod8/NEUCLSS.p_disp_dyn_sched"
TERM = "Fall 2016 Semester"
# TERM = "Spring 2016 Semester"
# For example, "CS", "EECE"
DEPT = "CS"
# DEPT = "EECE"
os.umask(0133) # Read-write permission for user, read-only for others

def web_to_rawhtml(URL, TERM, DEPT):
  # Browser
  browser = mechanize.Browser()
  browser.open(URL)
  
  # for f in browser.forms(): print f # find forms, control names for each form
  TERM_ID = ""
  for line in browser.response().readlines():
    keyword = 'VALUE="'
    if keyword in line and TERM in line:
      start_idx = line.find(keyword) + len(keyword)
      TERM_ID = line[start_idx : line.find('"', start_idx)]
      break
  assert TERM_ID, '"'+TERM+'" not found'
  
  browser.select_form(nr=0)
  browser.form["STU_TERM_IN"] = [TERM_ID]
  browser.submit()
  
  browser.select_form(nr=0)
  # For the values of kind, list includes subtypes singlelist and multilist.
  # browser.form.controls exists if there is more than one such control.
  try:
    browser.form.find_control('sel_subj', kind='list').value = [DEPT]
  except mechanize._form.ItemNotFoundError:
    sys.exit('Department "'+DEPT+'" not found\n')
  browser.submit()
  
  return str( browser.response().read() )

def rawhtml_to_courses(text, TERM, DEPT):
  text = text.replace(' (<ABBR title= "Primary">P</ABBR>)', '') # del this part
  text = text.replace('<ABBR title = "To Be Announced">TBA</ABBR>', 'TBA')
  text = text.replace('TBA &nbsp;', 'TBA')
  pattern = r'<TH CLASS="ddtitle"[^>]*><A HREF=[^>]*>'
  raw_courses = re.split(pattern, text)[1:] # using regular expressions here
  # Skip 7900-, 8000- 9900-level courses
  raw_courses = [ course for course in raw_courses
                  if DEPT+" 99" not in course and DEPT+" 8" not in course
                                              and DEPT+" 79" not in course
                ]
  courses = []
  for course in raw_courses:
    fields = []
    fields += course.split(' - ')[:3]
    if 'Instructors:' in course:
      fields += course.split('Instructors: </SPAN>')[1].split(' \n')[:1]
    else:
      fields += ['TBD']
    fields += course.split('</TD>\n<TD CLASS="dddefault">')
    fields = [ fields[i] for i in [0,1,2,3,5,6,9,10] ]
    del fields[1]
    # Combine last two fields
    fields[-2] = str(fields[-1] + '(' + fields[-2] + ')')
    del fields[-1]
    # Combine two fields for time
    fields[-3] += ' ' + fields[-2]
    del fields[-2]
    notes = []
    for keyword in ["Hybrid", "Seattle"]:
      if keyword in course:
        notes.append( keyword )
    if notes:
      fields.append( "(" + ', '.join(notes) + ")" )
    courses.append(fields)
  return courses


def courses_to_txt(lists):
  txt = ""
  for course in courses:
    txt += '; '.join(course) + '\n'
  return txt

def courses_to_csv(lists):
  csv = '"Number";"Course Title";"Instructor(s)";"Time";"Enrolled(Capacity)";"(Notes)"\n'
  for course in lists:
    csv += ','.join(['"'+field.strip()+'"' for field in course])+'\n'
  return csv

def courses_to_html(lists):
  html = \
"""<!DOCTYPE html>
<html>"""
  html += "\n<title>" + DEPT + " Courses; " + TERM + "</title>\n"
  html += \
"""<body>

<table>
<tr><th>Number</th> <th>Course Title</th> <th>Instructor(s)</th> <th>Time</th> <th>Enrolled(Capacity)</th> <th>(Notes)</th></tr>
"""
  for course in lists:
    html += "<tr>\n" + '\n'.join(['  <td>'+cell.strip()+'</td>'
                                  for cell in course]) + '\n</tr>\n'
  html += \
"""</table>

</body>
</html>
"""
  return html


rawhtml = web_to_rawhtml(URL, TERM, DEPT)
courses = rawhtml_to_courses(rawhtml, TERM, DEPT)
txt = courses_to_txt(courses)
csv = courses_to_csv(courses)
html = courses_to_html(courses)

files_written = []
for output in [(txt,".txt"), (csv,".csv"), (html,".html")]:
  (data, filetype) = output
  filename = (DEPT + " " + TERM + filetype).replace(' ', '_')
  file = open(filename, 'w'); file.write(data); file.close()
  files_written.append(filename)

print ("FILES WRITTEN:  " + ', '.join(files_written))
