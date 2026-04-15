from django.contrib.auth import get_user_model
from django.db.models import Count, F, Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from tasks.models import Task

User = get_user_model()


class MyPerformanceView(APIView):
    """
    GET /api/v1/reports/my-performance/

    Employees  — always returns their own stats.
    Managers   — returns own stats by default; pass ?user_id=<id> to view a
                 direct report's stats.

    All counts are derived from a single .aggregate() call — no per-row loops.

    Response fields:
        total_tasks      int   — all non-deleted tasks assigned to the user
        done_tasks       int   — tasks with status='done'
        completion_rate  float — done / total * 100, rounded to 1 dp (0.0 if no tasks)
        on_time_count    int   — done tasks where done_at.date <= due_date
        late_count       int   — done tasks where done_at.date >  due_date
        user             obj   — {id, full_name, role} of the subject
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        subject = request.user

        # Managers/admins may query a team member via ?user_id=
        if request.user.role in ['manager', 'admin']:
            user_id = request.query_params.get('user_id', '').strip()
            if user_id:
                try:
                    target = User.objects.get(id=int(user_id), is_active=True)
                except (User.DoesNotExist, ValueError):
                    return Response(
                        {'error': 'User not found.'},
                        status=status.HTTP_404_NOT_FOUND,
                    )
                # Managers can only see their own direct reports
                if request.user.role == 'manager' and target.manager_id != request.user.id:
                    return Response(
                        {'error': 'You can only view performance for your direct reports.'},
                        status=status.HTTP_403_FORBIDDEN,
                    )
                subject = target

        qs = Task.objects.filter(assigned_to=subject, is_deleted=False)

        # One aggregate call — four counts in one SQL query
        stats = qs.aggregate(
            total_tasks=Count('id'),
            done_tasks=Count('id', filter=Q(status='done')),
            on_time_count=Count(
                'id',
                filter=Q(
                    status='done',
                    done_at__isnull=False,
                    due_date__isnull=False,
                    done_at__date__lte=F('due_date'),
                ),
            ),
            late_count=Count(
                'id',
                filter=Q(
                    status='done',
                    done_at__isnull=False,
                    due_date__isnull=False,
                    done_at__date__gt=F('due_date'),
                ),
            ),
        )

        total = stats['total_tasks']
        done  = stats['done_tasks']
        completion_rate = round(done / total * 100, 1) if total > 0 else 0.0

        return Response({
            'total_tasks':     total,
            'done_tasks':      done,
            'completion_rate': completion_rate,
            'on_time_count':   stats['on_time_count'],
            'late_count':      stats['late_count'],
            'user': {
                'id':        subject.id,
                'full_name': f'{subject.first_name} {subject.last_name}'.strip() or subject.username,
                'role':      subject.role,
            },
        })
