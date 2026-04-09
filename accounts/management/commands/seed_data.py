from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from tasks.models import Task, TaskStatusHistory, TaskAssignment, TaskComment
from notifications.models import Notification
from core.models import SystemSetting
from datetime import date, timedelta

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed database with sample data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Clearing old data...')
        Notification.objects.all().delete()
        TaskComment.objects.all().delete()
        TaskAssignment.objects.all().delete()
        TaskStatusHistory.objects.all().delete()
        Task.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()

        self.stdout.write('Creating users...')

        # ── C-Suite (admin) ──────────────────────────────
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

        # ── Software Dept ────────────────────────────────
        # Manager
        vikram = User.objects.create_user(
            username='vikram.nair',
            email='vikram@taskflow.com',
            password='Test@1234',
            first_name='Vikram',
            last_name='Nair',
            role='manager',
            department='Software',
        )

        # Team Lead — Backend
        priya = User.objects.create_user(
            username='priya.sharma',
            email='priya@taskflow.com',
            password='Test@1234',
            first_name='Priya',
            last_name='Sharma',
            role='manager',
            department='Software',
        )

        # Team Lead — Frontend
        arjun = User.objects.create_user(
            username='arjun.desai',
            email='arjun@taskflow.com',
            password='Test@1234',
            first_name='Arjun',
            last_name='Desai',
            role='manager',
            department='Software',
        )

        # Backend employees
        rahul = User.objects.create_user(
            username='rahul.kumar',
            email='rahul@taskflow.com',
            password='Test@1234',
            first_name='Rahul',
            last_name='Kumar',
            role='employee',
            department='Software',
        )

        sneha = User.objects.create_user(
            username='sneha.patel',
            email='sneha@taskflow.com',
            password='Test@1234',
            first_name='Sneha',
            last_name='Patel',
            role='employee',
            department='Software',
        )

        # Frontend employees
        karan = User.objects.create_user(
            username='karan.singh',
            email='karan@taskflow.com',
            password='Test@1234',
            first_name='Karan',
            last_name='Singh',
            role='employee',
            department='Software',
        )

        pooja = User.objects.create_user(
            username='pooja.verma',
            email='pooja@taskflow.com',
            password='Test@1234',
            first_name='Pooja',
            last_name='Verma',
            role='employee',
            department='Software',
        )

        # ── Marketing Dept ───────────────────────────────
        # Manager
        neha = User.objects.create_user(
            username='neha.joshi',
            email='neha@taskflow.com',
            password='Test@1234',
            first_name='Neha',
            last_name='Joshi',
            role='manager',
            department='Marketing',
        )

        # Team Lead
        amit = User.objects.create_user(
            username='amit.kulkarni',
            email='amit@taskflow.com',
            password='Test@1234',
            first_name='Amit',
            last_name='Kulkarni',
            role='manager',
            department='Marketing',
        )

        # Employees
        divya = User.objects.create_user(
            username='divya.iyer',
            email='divya@taskflow.com',
            password='Test@1234',
            first_name='Divya',
            last_name='Iyer',
            role='employee',
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
        )

        # ── Accounts Dept ────────────────────────────────
        # Manager
        suresh = User.objects.create_user(
            username='suresh.gupta',
            email='suresh@taskflow.com',
            password='Test@1234',
            first_name='Suresh',
            last_name='Gupta',
            role='manager',
            department='Accounts',
        )

        # Employees
        meera = User.objects.create_user(
            username='meera.nair',
            email='meera@taskflow.com',
            password='Test@1234',
            first_name='Meera',
            last_name='Nair',
            role='employee',
            department='Accounts',
        )

        ankit = User.objects.create_user(
            username='ankit.shah',
            email='ankit@taskflow.com',
            password='Test@1234',
            first_name='Ankit',
            last_name='Shah',
            role='employee',
            department='Accounts',
        )

        # ── Operations Dept ──────────────────────────────
        # Manager
        ravi = User.objects.create_user(
            username='ravi.menon',
            email='ravi@taskflow.com',
            password='Test@1234',
            first_name='Ravi',
            last_name='Menon',
            role='manager',
            department='Operations',
        )

        # Employees
        kavya = User.objects.create_user(
            username='kavya.reddy',
            email='kavya@taskflow.com',
            password='Test@1234',
            first_name='Kavya',
            last_name='Reddy',
            role='employee',
            department='Operations',
        )

        rohit = User.objects.create_user(
            username='rohit.pandey',
            email='rohit@taskflow.com',
            password='Test@1234',
            first_name='Rohit',
            last_name='Pandey',
            role='employee',
            department='Operations',
        )

        self.stdout.write('Creating tasks...')

        # ── Software tasks ───────────────────────────────
        t1 = Task.objects.create(
            title='Fix login session timeout bug',
            description='Users logged out after 10 mins. Investigate JWT refresh logic.',
            status='in_progress', priority='high',
            due_date=date.today() + timedelta(days=4),
            assigned_to=rahul, created_by=priya,
        )
        t2 = Task.objects.create(
            title='Q2 backend architecture proposal',
            description='Draft architecture document for Q2 feature set including caching strategy.',
            status='in_progress', priority='high',
            due_date=date.today() + timedelta(days=2),
            assigned_to=rahul, created_by=priya,
        )
        t3 = Task.objects.create(
            title='Test coverage report',
            description='Generate and submit test coverage report for this sprint.',
            status='todo', priority='high',
            due_date=date.today() - timedelta(days=2),
            assigned_to=rahul, created_by=priya,
        )
        t4 = Task.objects.create(
            title='API performance audit',
            description='Run EXPLAIN ANALYZE on heavy queries and fix slow endpoints.',
            status='in_progress', priority='high',
            due_date=date.today() - timedelta(days=3),
            assigned_to=sneha, created_by=priya,
        )
        t5 = Task.objects.create(
            title='Set up CI/CD pipeline',
            description='Configure GitHub Actions for automated testing and deployment.',
            status='done', priority='high',
            due_date=date.today() - timedelta(days=20),
            assigned_to=rahul, created_by=priya,
        )
        t6 = Task.objects.create(
            title='Redesign dashboard UI',
            description='Redesign employee dashboard based on latest wireframes.',
            status='in_progress', priority='medium',
            due_date=date.today() + timedelta(days=5),
            assigned_to=karan, created_by=arjun,
        )
        t7 = Task.objects.create(
            title='Implement responsive sidebar',
            description='Make sidebar collapse on mobile screens below 768px.',
            status='todo', priority='medium',
            due_date=date.today() + timedelta(days=7),
            assigned_to=pooja, created_by=arjun,
        )

        # ── Marketing tasks ──────────────────────────────
        t8 = Task.objects.create(
            title='Q2 social media calendar',
            description='Plan and schedule social media posts for Q2.',
            status='in_progress', priority='medium',
            due_date=date.today() + timedelta(days=3),
            assigned_to=divya, created_by=amit,
        )
        t9 = Task.objects.create(
            title='Product launch email campaign',
            description='Design and send product launch email to 10k subscribers.',
            status='todo', priority='high',
            due_date=date.today() + timedelta(days=6),
            assigned_to=riya, created_by=neha,
        )
        t10 = Task.objects.create(
            title='Competitor analysis report',
            description='Research top 5 competitors and prepare analysis report.',
            status='done', priority='medium',
            due_date=date.today() - timedelta(days=5),
            assigned_to=divya, created_by=neha,
        )

        # ── Accounts tasks ───────────────────────────────
        t11 = Task.objects.create(
            title='Monthly GST filing',
            description='Prepare and submit GST returns for March 2026.',
            status='in_progress', priority='high',
            due_date=date.today() + timedelta(days=1),
            assigned_to=meera, created_by=suresh,
        )
        t12 = Task.objects.create(
            title='Q1 financial report',
            description='Compile Q1 financial statements for board review.',
            status='todo', priority='high',
            due_date=date.today() - timedelta(days=1),
            assigned_to=ankit, created_by=suresh,
        )

        # ── Operations tasks ─────────────────────────────
        t13 = Task.objects.create(
            title='Office supplies procurement',
            description='Order office supplies for April. Budget: ₹15,000.',
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

        TaskStatusHistory.objects.create(task=t1, changed_by=rahul, old_status='todo', new_status='in_progress')
        TaskStatusHistory.objects.create(task=t2, changed_by=rahul, old_status='todo', new_status='in_progress')
        TaskStatusHistory.objects.create(task=t4, changed_by=sneha, old_status='todo', new_status='in_progress')
        TaskStatusHistory.objects.create(task=t5, changed_by=rahul, old_status='todo', new_status='in_progress')
        TaskStatusHistory.objects.create(task=t5, changed_by=rahul, old_status='in_progress', new_status='done')
        TaskStatusHistory.objects.create(task=t6, changed_by=karan, old_status='todo', new_status='in_progress')
        TaskStatusHistory.objects.create(task=t8, changed_by=divya, old_status='todo', new_status='in_progress')
        TaskStatusHistory.objects.create(task=t10, changed_by=divya, old_status='todo', new_status='in_progress')
        TaskStatusHistory.objects.create(task=t10, changed_by=divya, old_status='in_progress', new_status='done')
        TaskStatusHistory.objects.create(task=t11, changed_by=meera, old_status='todo', new_status='in_progress')
        TaskStatusHistory.objects.create(task=t13, changed_by=kavya, old_status='todo', new_status='in_progress')
        TaskStatusHistory.objects.create(task=t13, changed_by=kavya, old_status='in_progress', new_status='done')
        TaskStatusHistory.objects.create(task=t14, changed_by=rohit, old_status='todo', new_status='in_progress')

        self.stdout.write('Creating assignments...')

        for task in [t1, t2, t3, t4, t5]:
            TaskAssignment.objects.create(task=task, assigned_to=task.assigned_to, assigned_by=priya)
        for task in [t6, t7]:
            TaskAssignment.objects.create(task=task, assigned_to=task.assigned_to, assigned_by=arjun)
        for task in [t8, t10]:
            TaskAssignment.objects.create(task=task, assigned_to=task.assigned_to, assigned_by=amit)
        TaskAssignment.objects.create(task=t9, assigned_to=riya, assigned_by=neha)
        for task in [t11, t12]:
            TaskAssignment.objects.create(task=task, assigned_to=task.assigned_to, assigned_by=suresh)
        TaskAssignment.objects.create(task=t13, assigned_to=kavya, assigned_by=ravi)
        TaskAssignment.objects.create(task=t14, assigned_to=rohit, assigned_by=ravi)

        self.stdout.write('Creating comments...')

        TaskComment.objects.create(task=t1, author=rahul, body='Reproduced — refresh token not sent after 9 mins. Looks like cookie expiry mismatch.')
        TaskComment.objects.create(task=t1, author=priya, body='Check ACCESS_TOKEN_LIFETIME in simplejwt config. Should be 60 mins not 10.')
        TaskComment.objects.create(task=t3, author=rahul, body='Blocked — waiting for QA to share coverage baseline from last sprint.')
        TaskComment.objects.create(task=t4, author=sneha, body='Found sequential scan on tasks table — missing index on assigned_to + status.')
        TaskComment.objects.create(task=t11, author=meera, body='Draft ready. Need Suresh sir to review before final submission.')
        TaskComment.objects.create(task=t12, author=ankit, body='Pending data from Marketing and Operations teams.')

        self.stdout.write('Creating notifications...')

        Notification.objects.create(user=rahul, type='task_assigned', title='New task: Fix login session timeout bug', message='Assigned by Priya Sharma', task=t1, is_read=True)
        Notification.objects.create(user=rahul, type='task_overdue', title='Overdue: Test coverage report is 2 days late', message='Please update the status or complete the task.', task=t3, is_read=False)
        Notification.objects.create(user=rahul, type='task_due_reminder', title='Due tomorrow: Q2 architecture proposal', message='This task is due tomorrow.', task=t2, is_read=False)
        Notification.objects.create(user=sneha, type='task_assigned', title='New task: API performance audit', message='Assigned by Priya Sharma', task=t4, is_read=True)
        Notification.objects.create(user=sneha, type='task_overdue', title='Overdue: API performance audit is 3 days late', message='Please update or complete the task.', task=t4, is_read=False)
        Notification.objects.create(user=meera, type='task_due_reminder', title='Due tomorrow: Monthly GST filing', message='This task is due tomorrow.', task=t11, is_read=False)
        Notification.objects.create(user=ankit, type='task_overdue', title='Overdue: Q1 financial report is 1 day late', message='Please update or complete the task.', task=t12, is_read=False)
        Notification.objects.create(user=divya, type='task_assigned', title='New task: Q2 social media calendar', message='Assigned by Amit Kulkarni', task=t8, is_read=True)
        Notification.objects.create(user=rohit, type='task_assigned', title='New task: Vendor contract renewal', message='Assigned by Ravi Menon', task=t14, is_read=True)

        self.stdout.write('Creating system settings...')

        SystemSetting.objects.get_or_create(key='google_sso_enabled', defaults={'value': 'true', 'description': 'Allow Google OAuth2 login', 'updated_by': ceo})
        SystemSetting.objects.get_or_create(key='overdue_notif_enabled', defaults={'value': 'true', 'description': 'Send overdue notifications', 'updated_by': ceo})
        SystemSetting.objects.get_or_create(key='reminder_notif_enabled', defaults={'value': 'true', 'description': 'Send due date reminders', 'updated_by': ceo})
        SystemSetting.objects.get_or_create(key='maintenance_mode', defaults={'value': 'false', 'description': 'Show maintenance banner', 'updated_by': ceo})

        self.stdout.write(self.style.SUCCESS('\nSeed data created successfully!'))
        self.stdout.write('─────────────────────────────────')
        self.stdout.write('Test credentials  (password: Test@1234)')
        self.stdout.write('─────────────────────────────────')
        self.stdout.write('CEO      → ceo@taskflow.com')
        self.stdout.write('CFO      → cfo@taskflow.com')
        self.stdout.write('Manager  → vikram@taskflow.com  (Software)')
        self.stdout.write('Manager  → neha@taskflow.com    (Marketing)')
        self.stdout.write('Manager  → suresh@taskflow.com  (Accounts)')
        self.stdout.write('Manager  → ravi@taskflow.com    (Operations)')
        self.stdout.write('TL       → priya@taskflow.com   (Backend)')
        self.stdout.write('TL       → arjun@taskflow.com   (Frontend)')
        self.stdout.write('TL       → amit@taskflow.com    (Marketing)')
        self.stdout.write('Employee → rahul@taskflow.com')
        self.stdout.write('Employee → sneha@taskflow.com')
        self.stdout.write('Employee → karan@taskflow.com')
        self.stdout.write('Employee → pooja@taskflow.com')
        self.stdout.write('Employee → divya@taskflow.com')
        self.stdout.write('Employee → riya@taskflow.com')
        self.stdout.write('Employee → meera@taskflow.com')
        self.stdout.write('Employee → ankit@taskflow.com')
        self.stdout.write('Employee → kavya@taskflow.com')
        self.stdout.write('Employee → rohit@taskflow.com')