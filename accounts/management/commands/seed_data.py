from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from tasks.models import Task, TaskStatusHistory, TaskAssignment, TaskComment
from notifications.models import Notification
from datetime import date, timedelta

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed database with sample data (deletes all non-superuser data first)'

    def handle(self, *args, **kwargs):
        self.stdout.write('Clearing old data...')
        Notification.objects.all().delete()
        TaskComment.objects.all().delete()
        TaskAssignment.objects.all().delete()
        TaskStatusHistory.objects.all().delete()
        Task.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()

        self.stdout.write('Creating users...')

        # ── C-Suite ──────────────────────────────────────────────────────────
        ceo = User.objects.create_user(
            username='rajesh.mehta',
            email='ceo@taskflow.com',
            password='Test@1234',
            first_name='Rajesh',
            last_name='Mehta',
            role='admin',
            department='Executive',
            is_staff=True,
        )

        cfo = User.objects.create_user(
            username='sunita.agarwal',
            email='cfo@taskflow.com',
            password='Test@1234',
            first_name='Sunita',
            last_name='Agarwal',
            role='admin',
            department='Executive',
            is_staff=True,
        )

        cto = User.objects.create_user(
            username='vikram.nair',
            email='cto@taskflow.com',
            password='Test@1234',
            first_name='Vikram',
            last_name='Nair',
            role='admin',
            department='Executive',
            is_staff=True,
        )

        # ── Software — Backend Team ───────────────────────────────────────────
        priya = User.objects.create_user(
            username='priya.sharma',
            email='priya@taskflow.com',
            password='Test@1234',
            first_name='Priya',
            last_name='Sharma',
            role='manager',
            department='Software',
        )

        rahul = User.objects.create_user(
            username='rahul.kumar',
            email='rahul@taskflow.com',
            password='Test@1234',
            first_name='Rahul',
            last_name='Kumar',
            role='employee',
            department='Software',
            manager=priya,
        )

        sneha = User.objects.create_user(
            username='sneha.patel',
            email='sneha@taskflow.com',
            password='Test@1234',
            first_name='Sneha',
            last_name='Patel',
            role='employee',
            department='Software',
            manager=priya,
        )

        # ── Software — Frontend Team ──────────────────────────────────────────
        arjun = User.objects.create_user(
            username='arjun.desai',
            email='arjun@taskflow.com',
            password='Test@1234',
            first_name='Arjun',
            last_name='Desai',
            role='manager',
            department='Software',
        )

        karan = User.objects.create_user(
            username='karan.singh',
            email='karan@taskflow.com',
            password='Test@1234',
            first_name='Karan',
            last_name='Singh',
            role='employee',
            department='Software',
            manager=arjun,
        )

        pooja = User.objects.create_user(
            username='pooja.verma',
            email='pooja@taskflow.com',
            password='Test@1234',
            first_name='Pooja',
            last_name='Verma',
            role='employee',
            department='Software',
            manager=arjun,
        )

        # ── Software — QA Team ────────────────────────────────────────────────
        deepak = User.objects.create_user(
            username='deepak.joshi',
            email='deepak@taskflow.com',
            password='Test@1234',
            first_name='Deepak',
            last_name='Joshi',
            role='manager',
            department='Software',
        )

        tanvi = User.objects.create_user(
            username='tanvi.rao',
            email='tanvi@taskflow.com',
            password='Test@1234',
            first_name='Tanvi',
            last_name='Rao',
            role='employee',
            department='Software',
            manager=deepak,
        )

        akash = User.objects.create_user(
            username='akash.tiwari',
            email='akash@taskflow.com',
            password='Test@1234',
            first_name='Akash',
            last_name='Tiwari',
            role='employee',
            department='Software',
            manager=deepak,
        )

        # ── Software — DevOps Team ────────────────────────────────────────────
        nisha = User.objects.create_user(
            username='nisha.bhat',
            email='nisha@taskflow.com',
            password='Test@1234',
            first_name='Nisha',
            last_name='Bhat',
            role='manager',
            department='Software',
        )

        saurabh = User.objects.create_user(
            username='saurabh.yadav',
            email='saurabh@taskflow.com',
            password='Test@1234',
            first_name='Saurabh',
            last_name='Yadav',
            role='employee',
            department='Software',
            manager=nisha,
        )

        # ── Marketing — Content & Social Team ────────────────────────────────
        neha = User.objects.create_user(
            username='neha.joshi',
            email='neha@taskflow.com',
            password='Test@1234',
            first_name='Neha',
            last_name='Joshi',
            role='manager',
            department='Marketing',
        )

        riya = User.objects.create_user(
            username='riya.bose',
            email='riya@taskflow.com',
            password='Test@1234',
            first_name='Riya',
            last_name='Bose',
            role='employee',
            department='Marketing',
            manager=neha,
        )

        # ── Marketing — Growth & Campaigns Team ──────────────────────────────
        amit = User.objects.create_user(
            username='amit.kulkarni',
            email='amit@taskflow.com',
            password='Test@1234',
            first_name='Amit',
            last_name='Kulkarni',
            role='manager',
            department='Marketing',
        )

        divya = User.objects.create_user(
            username='divya.iyer',
            email='divya@taskflow.com',
            password='Test@1234',
            first_name='Divya',
            last_name='Iyer',
            role='employee',
            department='Marketing',
            manager=amit,
        )

        # ── Finance Dept ──────────────────────────────────────────────────────
        suresh = User.objects.create_user(
            username='suresh.gupta',
            email='suresh@taskflow.com',
            password='Test@1234',
            first_name='Suresh',
            last_name='Gupta',
            role='manager',
            department='Finance',
        )

        meera = User.objects.create_user(
            username='meera.nair',
            email='meera@taskflow.com',
            password='Test@1234',
            first_name='Meera',
            last_name='Nair',
            role='employee',
            department='Finance',
            manager=suresh,
        )

        ankit = User.objects.create_user(
            username='ankit.shah',
            email='ankit@taskflow.com',
            password='Test@1234',
            first_name='Ankit',
            last_name='Shah',
            role='employee',
            department='Finance',
            manager=suresh,
        )

        # ── Operations Dept ───────────────────────────────────────────────────
        ravi = User.objects.create_user(
            username='ravi.menon',
            email='ravi@taskflow.com',
            password='Test@1234',
            first_name='Ravi',
            last_name='Menon',
            role='manager',
            department='Operations',
        )

        kavya = User.objects.create_user(
            username='kavya.reddy',
            email='kavya@taskflow.com',
            password='Test@1234',
            first_name='Kavya',
            last_name='Reddy',
            role='employee',
            department='Operations',
            manager=ravi,
        )

        rohit = User.objects.create_user(
            username='rohit.pandey',
            email='rohit@taskflow.com',
            password='Test@1234',
            first_name='Rohit',
            last_name='Pandey',
            role='employee',
            department='Operations',
            manager=ravi,
        )

        self.stdout.write('Creating tasks...')

        # ── Software — Backend tasks ──────────────────────────────────────────
        t1 = Task.objects.create(
            title='Fix login session timeout bug',
            description='Users are being logged out after 10 mins. Investigate JWT refresh logic and token expiry mismatch.',
            status='in_progress', priority='high',
            due_date=date.today() + timedelta(days=4),
            assigned_to=rahul, created_by=priya,
        )
        t2 = Task.objects.create(
            title='Q2 backend architecture proposal',
            description='Draft architecture document for Q2 feature set including caching strategy and service boundaries.',
            status='in_progress', priority='high',
            due_date=date.today() + timedelta(days=2),
            assigned_to=rahul, created_by=priya,
        )
        t3 = Task.objects.create(
            title='Test coverage report',
            description='Generate and submit test coverage report for the current sprint.',
            status='todo', priority='high',
            due_date=date.today() - timedelta(days=2),
            assigned_to=rahul, created_by=priya,
        )
        t4 = Task.objects.create(
            title='API performance audit',
            description='Run EXPLAIN ANALYZE on heavy queries and fix slow endpoints above 500ms threshold.',
            status='in_progress', priority='high',
            due_date=date.today() - timedelta(days=3),
            assigned_to=sneha, created_by=priya,
        )
        t5 = Task.objects.create(
            title='Set up CI/CD pipeline',
            description='Configure GitHub Actions for automated testing and deployment to staging.',
            status='done', priority='high',
            due_date=date.today() - timedelta(days=20),
            assigned_to=rahul, created_by=priya,
        )

        # ── Software — Frontend tasks ─────────────────────────────────────────
        t6 = Task.objects.create(
            title='Redesign dashboard UI',
            description='Redesign employee dashboard based on latest Figma wireframes from design team.',
            status='in_progress', priority='medium',
            due_date=date.today() + timedelta(days=5),
            assigned_to=karan, created_by=arjun,
        )
        t7 = Task.objects.create(
            title='Implement responsive sidebar',
            description='Make sidebar collapse gracefully on mobile screens below 768px.',
            status='todo', priority='medium',
            due_date=date.today() + timedelta(days=7),
            assigned_to=pooja, created_by=arjun,
        )

        # ── Software — QA tasks ───────────────────────────────────────────────
        t16 = Task.objects.create(
            title='Set up QA automation framework',
            description='Evaluate and configure Pytest + Selenium automation framework for the regression suite.',
            status='in_progress', priority='high',
            due_date=date.today() + timedelta(days=6),
            assigned_to=tanvi, created_by=deepak,
        )
        t17 = Task.objects.create(
            title='Sprint regression testing',
            description='Execute full regression test suite for Sprint 12 release candidate.',
            status='todo', priority='high',
            due_date=date.today() + timedelta(days=3),
            assigned_to=akash, created_by=deepak,
        )
        t18 = Task.objects.create(
            title='QA sign-off for API performance audit',
            description='Validate fixed endpoints post-performance audit. Log defects if thresholds are still breached.',
            status='todo', priority='medium',
            due_date=date.today() + timedelta(days=5),
            assigned_to=tanvi, created_by=deepak,
        )

        # ── Software — DevOps tasks ───────────────────────────────────────────
        t19 = Task.objects.create(
            title='Kubernetes cluster migration',
            description='Migrate staging environment from Docker Compose to K8s. Document rollback plan.',
            status='in_progress', priority='high',
            due_date=date.today() + timedelta(days=9),
            assigned_to=saurabh, created_by=nisha,
        )
        t20 = Task.objects.create(
            title='Secrets management audit',
            description='Audit all hardcoded secrets in config files and migrate to Vault/env-based secrets.',
            status='todo', priority='high',
            due_date=date.today() + timedelta(days=12),
            assigned_to=saurabh, created_by=nisha,
        )

        # ── CTO-level task (assigned by CEO) ─────────────────────────────────
        t15 = Task.objects.create(
            title='Q2 software roadmap review',
            description='Consolidate Q2 roadmap across Backend, Frontend, QA, and DevOps teams. Present to CEO by end of week.',
            status='in_progress', priority='high',
            due_date=date.today() + timedelta(days=10),
            assigned_to=cto, created_by=ceo,
        )

        # ── Marketing tasks ───────────────────────────────────────────────────
        t8 = Task.objects.create(
            title='Q2 social media calendar',
            description='Plan and schedule social media posts across LinkedIn, Twitter, and Instagram for Q2.',
            status='in_progress', priority='medium',
            due_date=date.today() + timedelta(days=3),
            assigned_to=divya, created_by=amit,
        )
        t9 = Task.objects.create(
            title='Product launch email campaign',
            description='Design and send product launch email to 10k subscribers. A/B test subject lines.',
            status='todo', priority='high',
            due_date=date.today() + timedelta(days=6),
            assigned_to=riya, created_by=neha,
        )
        t10 = Task.objects.create(
            title='Competitor analysis report',
            description='Research top 5 competitors and prepare a structured analysis report for leadership.',
            status='done', priority='medium',
            due_date=date.today() - timedelta(days=5),
            assigned_to=divya, created_by=neha,
        )

        # ── Finance tasks ─────────────────────────────────────────────────────
        t11 = Task.objects.create(
            title='Monthly GST filing',
            description='Prepare and submit GST returns for March 2026. Deadline: 20th April.',
            status='in_progress', priority='high',
            due_date=date.today() + timedelta(days=1),
            assigned_to=meera, created_by=suresh,
        )
        t12 = Task.objects.create(
            title='Q1 financial report',
            description='Compile Q1 financial statements for board review. Coordinate with Marketing and Operations for actuals.',
            status='todo', priority='high',
            due_date=date.today() - timedelta(days=1),
            assigned_to=ankit, created_by=suresh,
        )

        # ── Operations tasks ──────────────────────────────────────────────────
        t13 = Task.objects.create(
            title='Office supplies procurement',
            description='Order office supplies for April. Approved budget: ₹15,000.',
            status='done', priority='low',
            due_date=date.today() - timedelta(days=10),
            assigned_to=kavya, created_by=ravi,
        )
        t14 = Task.objects.create(
            title='Vendor contract renewal',
            description='Review and renew contracts with 3 key vendors before April 15.',
            status='in_progress', priority='high',
            due_date=date.today() + timedelta(days=8),
            assigned_to=rohit, created_by=ravi,
        )

        self.stdout.write('Creating status history...')

        TaskStatusHistory.objects.create(task=t1,  changed_by=rahul,   old_status='todo',        new_status='in_progress')
        TaskStatusHistory.objects.create(task=t2,  changed_by=rahul,   old_status='todo',        new_status='in_progress')
        TaskStatusHistory.objects.create(task=t4,  changed_by=sneha,   old_status='todo',        new_status='in_progress')
        TaskStatusHistory.objects.create(task=t5,  changed_by=rahul,   old_status='todo',        new_status='in_progress')
        TaskStatusHistory.objects.create(task=t5,  changed_by=rahul,   old_status='in_progress', new_status='done')
        TaskStatusHistory.objects.create(task=t6,  changed_by=karan,   old_status='todo',        new_status='in_progress')
        TaskStatusHistory.objects.create(task=t8,  changed_by=divya,   old_status='todo',        new_status='in_progress')
        TaskStatusHistory.objects.create(task=t10, changed_by=divya,   old_status='todo',        new_status='in_progress')
        TaskStatusHistory.objects.create(task=t10, changed_by=divya,   old_status='in_progress', new_status='done')
        TaskStatusHistory.objects.create(task=t11, changed_by=meera,   old_status='todo',        new_status='in_progress')
        TaskStatusHistory.objects.create(task=t13, changed_by=kavya,   old_status='todo',        new_status='in_progress')
        TaskStatusHistory.objects.create(task=t13, changed_by=kavya,   old_status='in_progress', new_status='done')
        TaskStatusHistory.objects.create(task=t14, changed_by=rohit,   old_status='todo',        new_status='in_progress')
        TaskStatusHistory.objects.create(task=t15, changed_by=cto,     old_status='todo',        new_status='in_progress')
        TaskStatusHistory.objects.create(task=t16, changed_by=tanvi,   old_status='todo',        new_status='in_progress')
        TaskStatusHistory.objects.create(task=t19, changed_by=saurabh, old_status='todo',        new_status='in_progress')

        self.stdout.write('Creating assignments...')

        for task in [t1, t2, t3, t4, t5]:
            TaskAssignment.objects.create(task=task, assigned_to=task.assigned_to, assigned_by=priya)
        for task in [t6, t7]:
            TaskAssignment.objects.create(task=task, assigned_to=task.assigned_to, assigned_by=arjun)
        for task in [t16, t17, t18]:
            TaskAssignment.objects.create(task=task, assigned_to=task.assigned_to, assigned_by=deepak)
        for task in [t19, t20]:
            TaskAssignment.objects.create(task=task, assigned_to=task.assigned_to, assigned_by=nisha)
        TaskAssignment.objects.create(task=t15,  assigned_to=cto,   assigned_by=ceo)
        for task in [t8, t10]:
            TaskAssignment.objects.create(task=task, assigned_to=task.assigned_to, assigned_by=amit)
        TaskAssignment.objects.create(task=t9,   assigned_to=riya,  assigned_by=neha)
        for task in [t11, t12]:
            TaskAssignment.objects.create(task=task, assigned_to=task.assigned_to, assigned_by=suresh)
        TaskAssignment.objects.create(task=t13,  assigned_to=kavya, assigned_by=ravi)
        TaskAssignment.objects.create(task=t14,  assigned_to=rohit, assigned_by=ravi)

        self.stdout.write('Creating comments...')

        TaskComment.objects.create(task=t1,  author=rahul,   body='Reproduced — refresh token not being sent after 9 mins. Looks like cookie expiry mismatch.')
        TaskComment.objects.create(task=t1,  author=priya,   body='Check ACCESS_TOKEN_LIFETIME in simplejwt config. Should be 60 mins not 10.')
        TaskComment.objects.create(task=t3,  author=rahul,   body='Blocked — waiting for QA team to share coverage baseline from last sprint.')
        TaskComment.objects.create(task=t4,  author=sneha,   body='Found sequential scan on tasks table — missing index on assigned_to + status composite.')
        TaskComment.objects.create(task=t11, author=meera,   body='Draft ready. Need Suresh sir to review before final submission.')
        TaskComment.objects.create(task=t12, author=ankit,   body='Pending actuals from Marketing and Operations teams.')
        TaskComment.objects.create(task=t15, author=cto,     body='Backend roadmap received from Priya. Waiting on Arjun for frontend items and Deepak for QA timelines.')
        TaskComment.objects.create(task=t16, author=tanvi,   body='Pytest + Selenium shortlisted. Setting up base test runner and fixtures this week.')
        TaskComment.objects.create(task=t19, author=saurabh, body='Staging namespace created. Working on Helm chart templates for the app services.')

        self.stdout.write('Creating notifications...')

        Notification.objects.create(user=rahul,   type='task_assigned',     title='New task: Fix login session timeout bug',        message='Assigned by Priya Sharma',       task=t1,  is_read=True)
        Notification.objects.create(user=rahul,   type='task_overdue',      title='Overdue: Test coverage report is 2 days late',   message='Please update the status or complete the task.', task=t3, is_read=False)
        Notification.objects.create(user=rahul,   type='task_due_reminder', title='Due soon: Q2 architecture proposal',             message='This task is due in 2 days.',     task=t2,  is_read=False)
        Notification.objects.create(user=sneha,   type='task_assigned',     title='New task: API performance audit',                message='Assigned by Priya Sharma',       task=t4,  is_read=True)
        Notification.objects.create(user=sneha,   type='task_overdue',      title='Overdue: API performance audit is 3 days late',  message='Please update or complete the task.', task=t4, is_read=False)
        Notification.objects.create(user=meera,   type='task_due_reminder', title='Due tomorrow: Monthly GST filing',               message='This task is due tomorrow.',      task=t11, is_read=False)
        Notification.objects.create(user=ankit,   type='task_overdue',      title='Overdue: Q1 financial report is 1 day late',     message='Please update or complete the task.', task=t12, is_read=False)
        Notification.objects.create(user=divya,   type='task_assigned',     title='New task: Q2 social media calendar',             message='Assigned by Amit Kulkarni',      task=t8,  is_read=True)
        Notification.objects.create(user=rohit,   type='task_assigned',     title='New task: Vendor contract renewal',              message='Assigned by Ravi Menon',         task=t14, is_read=True)
        Notification.objects.create(user=cto,     type='task_assigned',     title='New task: Q2 software roadmap review',           message='Assigned by Rajesh Mehta (CEO)', task=t15, is_read=False)
        Notification.objects.create(user=tanvi,   type='task_assigned',     title='New task: Set up QA automation framework',       message='Assigned by Deepak Joshi',       task=t16, is_read=True)
        Notification.objects.create(user=akash,   type='task_assigned',     title='New task: Sprint regression testing',            message='Assigned by Deepak Joshi',       task=t17, is_read=False)
        Notification.objects.create(user=saurabh, type='task_assigned',     title='New task: Kubernetes cluster migration',         message='Assigned by Nisha Bhat',         task=t19, is_read=True)

        self.stdout.write(self.style.SUCCESS('\nSeed data created successfully!'))
        self.stdout.write('─' * 55)
        self.stdout.write('Test credentials  (password: Test@1234)')
        self.stdout.write('─' * 55)
        self.stdout.write('C-Suite (Executive)')
        self.stdout.write('  CEO  →  ceo@taskflow.com   (Rajesh Mehta)')
        self.stdout.write('  CFO  →  cfo@taskflow.com   (Sunita Agarwal)')
        self.stdout.write('  CTO  →  cto@taskflow.com   (Vikram Nair)')
        self.stdout.write('─' * 55)
        self.stdout.write('Software — Backend Team')
        self.stdout.write('  Lead     →  priya@taskflow.com   (Priya Sharma)')
        self.stdout.write('  Employee →  rahul@taskflow.com   (Rahul Kumar)')
        self.stdout.write('  Employee →  sneha@taskflow.com   (Sneha Patel)')
        self.stdout.write('Software — Frontend Team')
        self.stdout.write('  Lead     →  arjun@taskflow.com   (Arjun Desai)')
        self.stdout.write('  Employee →  karan@taskflow.com   (Karan Singh)')
        self.stdout.write('  Employee →  pooja@taskflow.com   (Pooja Verma)')
        self.stdout.write('Software — QA Team')
        self.stdout.write('  Lead     →  deepak@taskflow.com  (Deepak Joshi)')
        self.stdout.write('  Employee →  tanvi@taskflow.com   (Tanvi Rao)')
        self.stdout.write('  Employee →  akash@taskflow.com   (Akash Tiwari)')
        self.stdout.write('Software — DevOps Team')
        self.stdout.write('  Lead     →  nisha@taskflow.com   (Nisha Bhat)')
        self.stdout.write('  Employee →  saurabh@taskflow.com (Saurabh Yadav)')
        self.stdout.write('─' * 55)
        self.stdout.write('Marketing — Content & Social')
        self.stdout.write('  Lead     →  neha@taskflow.com    (Neha Joshi)')
        self.stdout.write('  Employee →  riya@taskflow.com    (Riya Bose)')
        self.stdout.write('Marketing — Growth & Campaigns')
        self.stdout.write('  Lead     →  amit@taskflow.com    (Amit Kulkarni)')
        self.stdout.write('  Employee →  divya@taskflow.com   (Divya Iyer)')
        self.stdout.write('─' * 55)
        self.stdout.write('Finance')
        self.stdout.write('  Lead     →  suresh@taskflow.com  (Suresh Gupta)')
        self.stdout.write('  Employee →  meera@taskflow.com   (Meera Nair)')
        self.stdout.write('  Employee →  ankit@taskflow.com   (Ankit Shah)')
        self.stdout.write('─' * 55)
        self.stdout.write('Operations')
        self.stdout.write('  Lead     →  ravi@taskflow.com    (Ravi Menon)')
        self.stdout.write('  Employee →  kavya@taskflow.com   (Kavya Reddy)')
        self.stdout.write('  Employee →  rohit@taskflow.com   (Rohit Pandey)')
        self.stdout.write('─' * 55)
