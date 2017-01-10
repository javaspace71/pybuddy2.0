"""TO-DO: Write a description of what this XBlock is."""

import pkg_resources
import logging
import urllib
import json

from xblock.core import XBlock
from xblock.fields import Scope, String, Dict, Float, Boolean, Integer
from xblock.fragment import Fragment
from xblockutils.resources import ResourceLoader
#from .utils import _, DummyTranslationService, FeedbackMessage, FeedbackMessages, ItemStats, StateMigration, Constants
from pylint import lint
from astroid import MANAGER
from pylint.reporters.text import TextReporter
from subprocess import Popen, PIPE, STDOUT, call, check_output

'''
from RestrictedPython import compile_restricted
from RestrictedPython.PrintCollector import PrintCollector
from RestrictedPython.Guards import safe_builtins
restricted_globals = dict(__builtins__ = safe_builtins)
_print_ = PrintCollector
'''
import shlex


LOG = logging.getLogger(__name__)
RESOURCE_LOADER = ResourceLoader(__name__)

class PythonBuddyXBlock(XBlock):
    """
    TO-DO: document what your XBlock does.
    """

    # Fields are defined on the class.  You can access them in your code as
    # self.<fieldname>.

    # TO-DO: delete count, and define your own fields.
    '''
    count = Integer(
        default=0, scope=Scope.user_state,
        help="A simple counter, to show something happening",
    )
    '''

    #Set fields for teacher's to customize the problem
    #Instructor has to type &#10; for new line, &#009; for new tab
    problem_data = String(
        display_name="Problem data",
        help="Python Problem",
        scope=Scope.content,
        default="asdfasdfasdfasdf",
    )


    max_attempts = Integer(
        display_name="Maximum attempts",
        help="Defines the number of times a student can try to answer this problem. If the value is not set, infinite attempts are allowed.",
        scope=Scope.settings,
        default=None,
    )

    weight = Float(
        display_name="Problem Weight",
        help="Defines the number of points the problem is worth.",
        scope=Scope.settings,
        default=1,
    )

    attempts = Integer(
        help="Number of attempts learner used",
        scope=Scope.user_state,
        default=0
    )

    completed = Boolean(
        help="Indicates whether a learner has completed the problem at least once",
        scope=Scope.user_state,
        default=False,
    )

    grade = Float(
        help="Keeps maximum score achieved by student",
        scope=Scope.user_state,
        default=0
    )


    # TO-DO: change this view to display your data your own way.
    def student_view(self, context):
        """
        The primary view of the PythonBuddyXBlock, shown to students
        when viewing courses.
        """
        context = {
            'fields': self.fields,
            'self': self,
            #'data': urllib.quote(json.dumps(self.data)),
        }
        fragment = Fragment()
        fragment.add_content(RESOURCE_LOADER.render_template('templates/html/pybuddy.html', context))
        css_urls = (
            'public/css/bootstrap.min.css',
            'public/css/style.css',
            'public/codemirror/lib/codemirror.css',
            'public/codemirror/lib/lint.css',
            'public/codemirror/addon/dialog.css'
        )
        #jquery might have errors since edx also loads jquery 
        js_urls = (
            #'public/js/jquery.js',
            'public/codemirror/lib/codemirror.js',
            'public/codemirror/lib/python.js',
            'public/codemirror/lib/lint.js',
            'public/js/cm-validator-remote.js',
            'public/codemirror/addon/search.js',
            'public/codemirror/addon/searchcursor.js',
            'public/codemirror/addon/dialog.js',
            'public/js/javascript.js'
        )
        for css_url in css_urls:
            fragment.add_css_url(self.runtime.local_resource_url(self, css_url))
        for js_url in js_urls:
            fragment.add_javascript_url(self.runtime.local_resource_url(self, js_url))

        fragment.initialize_js('PythonBuddyXBlock', self.get_configuration())
        return fragment

    def get_configuration(self):
        #All credit goes to drag and drop v.2
        """
        Get the configuration data for the student_view.
        The configuration is all the settings defined by the author, except for correct answers
        and feedback.
        """
        '''
        def items_without_answers():
            """
            Removes feedback and answer from items
            """
            items = copy.deepcopy(self.data.get('items', ''))
            for item in items:
                del item['feedback']
                # Use item.pop to remove both `item['zone']` and `item['zones']`; we don't have
                # a guarantee that either will be present, so we can't use `del`. Legacy instances
                # will have `item['zone']`, while current versions will have `item['zones']`.
                item.pop('zone', None)
                item.pop('zones', None)
                # Fall back on "backgroundImage" to be backward-compatible.
                image_url = item.get('imageURL') or item.get('backgroundImage')
                if image_url:
                    item['expandedImageURL'] = self._expand_static_url(image_url)
                else:
                    item['expandedImageURL'] = ''
            return items
        '''

        return {
            #"data":self.data,
            "max_attempts": self.max_attempts,
            "problem_data":self.problem_data,
            "graded": getattr(self, 'graded', False),
            #"weighted_max_score": self.max_score() * self.weight,
            # SDK doesn't supply url_name.
            "url_name": getattr(self, 'url_name', ''),
        }
    def author_view(self, context):
        context = {
            'fields': self.fields,
            'self': self,
            #'data': urllib.quote(json.dumps(self.data)),
        }
        fragment = Fragment()
        fragment.add_content(RESOURCE_LOADER.render_template('templates/html/pybuddy_edit.html', context))
        css_urls = (
            'public/css/bootstrap.min.css',
            'public/css/style.css',
            'public/codemirror/lib/codemirror.css',
            'public/codemirror/lib/lint.css',
            'public/codemirror/addon/dialog.css'
        )
        #jquery might have errors since edx also loads jquery 
        js_urls = (
            #'public/js/jquery.js',
            'public/codemirror/lib/codemirror.js',
            'public/codemirror/lib/python.js',
            'public/codemirror/lib/lint.js',
            'public/js/cm-validator-remote.js',
            'public/codemirror/addon/search.js',
            'public/codemirror/addon/searchcursor.js',
            'public/codemirror/addon/dialog.js',
            'public/js/javascript_edit.js'
        )
        for css_url in css_urls:
            fragment.add_css_url(self.runtime.local_resource_url(self, css_url))
        for js_url in js_urls:
            fragment.add_javascript_url(self.runtime.local_resource_url(self, js_url))

        fragment.initialize_js('PythonBuddyXBlock')
        return fragment

    def studio_view(self, context):
        #Code based on xblock drag an drop by the edx-solutions team
        #js_templates = loader.load_unicode('/templates/html/js_templates.html')
        # Get a 'html_id' string that is unique for this block.
        # We append it to HTML element ID attributes to ensure multiple instances of the DnDv2 block
        # on the same page don't share the same ID value.
        # We avoid using ID attributes in preference to classes, but sometimes we still need IDs to
        # connect 'for' and 'aria-describedby' attributes to the associated elements.
        id_suffix = self.location.html_id()  # pylint: disable=no-member
        #js_templates = js_templates.replace('{{id_suffix}}', id_suffix)
        context = {
            #'js_templates': js_templates,
            'id_suffix': id_suffix,
            'fields': self.fields,
            'self': self,
            #'data': urllib.quote(json.dumps(self.data)),
        }
        fragment = Fragment()
        fragment.add_content(RESOURCE_LOADER.render_template('templates/html/pybuddy_edit.html', context))
        css_urls = (
            'public/css/bootstrap.min.css',
            'public/css/style.css',
            'public/codemirror/lib/codemirror.css',
            'public/codemirror/lib/lint.css',
            'public/codemirror/addon/dialog.css'
        )
        #jquery might have errors since edx also loads jquery 
        js_urls = (
            #'public/js/jquery.js',
            'public/codemirror/lib/codemirror.js',
            'public/codemirror/lib/python.js',
            'public/codemirror/lib/lint.js',
            'public/js/cm-validator-remote.js',
            'public/codemirror/addon/search.js',
            'public/codemirror/addon/searchcursor.js',
            'public/codemirror/addon/dialog.js',
            'public/js/javascript_edit.js'
        )
        for css_url in css_urls:
            fragment.add_css_url(self.runtime.local_resource_url(self, css_url))
        for js_url in js_urls:
            fragment.add_javascript_url(self.runtime.local_resource_url(self, js_url))

        fragment.initialize_js('PythonBuddyXBlock')
        return fragment


    @XBlock.json_handler
    def studio_submit(self, submissions, suffix=''):
        """
        Handles studio save.
        """
        self.problem_data = submissions['problem_data']
        #self.max_attempts = submissions['max_attempts']
        #self.weight = float(submissions['weight'])
        #self.attempts = submissions['attempts']
        #self.completed = submissions['completed']
        #self.grade = float(submissions['grade'])

        return {
            'result': 'success',
        }

    @XBlock.json_handler
    def check_code(self, data, suffix=''):
        print "hi123"
        #Get textarea text from AJAX call
        text = data['text']
        print "hello"

        #Open temp file which will be parsed

        #changed to w+ from r+ originally
        f = open("error_test.py","w+")
        f.seek(0)
        f.write(text)
        f.truncate()
        f.close()

        #Writable Object that will be used as a TextReporter
        class WritableObject(object):
            def __init__(self):
                self.content = []
            def write(self, st):
                self.content.append(st)
            def read(self):
                return self.content

        #Remember that you can configure with a seperate file for more specific limitations => --rcfile=/path/to/config.file . 
        #See http://stackoverflow.com/a/10138997/4698963
        #Add "--disable=R,C" to ARGs to print only errors & warnings
        ARGS = ["-r","n", "--disable=R,C","--msg-template={path}:{line}: [{msg_id}({symbol}), {obj}] {msg}"]

        pylint_output = WritableObject()
        #Run Pylint, textreporter will redirect to writable object
        lint.Run(["error_test.py"]+ARGS, reporter=TextReporter(pylint_output), exit=False)
        pylint_list = pylint_output.content
        #Clear Cache. VERY IMPORTANT! This will make sure that there's no funky issues. See: http://stackoverflow.com/questions/2028268/invoking-pylint-programmatically#comment5393474_4803466 
        MANAGER.astroid_cache.clear()


        #Return json object, which is the pylint_output seperated by each newline
        return pylint_list

    #@XBlock.json_handler
    @XBlock.json_handler
    def run_code(self, data, suffix=''):
        print "run_test"
        '''
        #Open file and get unsafe code
        with open('error_test.py', 'r') as myfile:
            file_data = myfile.read()

        #print file_data
        #Use Restricted Python to make sure text is safe
        code = compile_restricted(file_data, '<string>', 'exec')

        # the text doesnt appear on stdout
        # The print collector collects it 
        #We can have access to the text using the printed variable though
        exec(code)
        return printed
        '''
        '''
        #Remember file path depends on Operating System 
        cmd = 'python error_test.py'
        #cmd = 'exec(code)'
        p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
        output = p.stdout.read()

        return output
        '''
        cmd = 'python  error_test.py'
        #call(shlex.split(cmd), shell=False)
        output = check_output(shlex.split(cmd), shell=False)
        #output = stdout.read()
        return output


        
        

    # TO-DO: change this to create the scenarios you'd like to see in the
    # workbench while developing your XBlock.
    @staticmethod
    def workbench_scenarios():
        """A canned scenario for display in the workbench."""
        return [
            ("PythonBuddyXBlock",
             """<pybuddy data="for i in range(5):&#10;&#009;print i"
                max_attempts="3"/>
             """),
            ("Multiple PythonBuddyXBlock",
             """<vertical_demo>
                <pybuddy/>
                <pybuddy/>
                <pybuddy/>
                </vertical_demo>
             """),
        ]
