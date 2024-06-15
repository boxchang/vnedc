import datetime
from django.contrib.auth.models import Permission
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth import authenticate
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.urls import reverse
from django.db.models import Q
from bases.views import index
from users.forms import CurrentCustomUserForm, CustomUser, UserInfoForm, Unit
from users.models import UserType


def add_permission(user, codename):
    perm = Permission.objects.get(codename=codename)
    user.user_permissions.add(perm)


def remove_permission(user, codename):
    perm = Permission.objects.get(codename=codename)
    user.user_permissions.remove(perm)


def register(request):
    '''
    Register a new user
    '''
    template = 'users/register.html'
    if request.method == 'GET':
        return render(request, template, {'userForm': CurrentCustomUserForm()})

    # POST
    userForm = CurrentCustomUserForm(request.POST)
    if not userForm.is_valid():
        return render(request, template, {'userForm': userForm})

    userForm.save()
    messages.success(request, '歡迎註冊')
    return redirect('register')


def login(request):
    if 'emp_no' in request.COOKIES:
        cookies_username = request.COOKIES['emp_no']

    if 'password' in request.COOKIES:
        cookies_password = request.COOKIES['password']

    '''
    Login an existing user
    '''
    template = 'users/login.html'
    if request.method == 'GET':
        next = request.GET.get('next')
        return render(request, template, locals())

    if request.method == 'POST':
        next_page = request.POST.get('next')
        if request.user.is_authenticated:
            if next_page != 'None':
                return HttpResponseRedirect(next_page)
            else:
                return index(request)
        else:
            # POST
            emp_no = request.POST.get('emp_no')
            password = request.POST.get('password')
            if not emp_no or not password:    # Server-side validation
                messages.error(request, '使用者名稱或密碼未填寫！')
                return render(request, template)

            user = authenticate(username=emp_no, password=password)
            if not user:    # authentication fails
                messages.error(request, '使用者名稱或密碼不正確！')
                return render(request, template)

            response = redirect(reverse('daily_info_create'))
            if request.POST.get('remember') == "on":
                response.set_cookie("emp_no", emp_no, expires=timezone.now()+datetime.timedelta(days=30))
                response.set_cookie("password", password, expires=timezone.now()+datetime.timedelta(days=30))
            else:
                response.delete_cookie("emp_no")
                response.delete_cookie("password")
            # login success
            auth_login(request, user)

            # messages.success(request, '登入成功')

            return response


def logout(request):
    '''
    Logout the user
    '''
    auth_logout(request)
    messages.success(request, '歡迎再度光臨')
    return redirect('login')


# Create
@login_required
def create(request):
    template = 'users/create.html'
    if request.method == 'GET':
        form = CurrentCustomUserForm()
        form.fields['password1'].required = True
        form.fields['password2'].required = True
        if not request.user.is_superuser:
            form.fields["user_type"].queryset = UserType.objects.filter(type_name="一般使用者").all()

        return render(request, template, {'userForm': form})

    if request.method == 'POST':
        form = CurrentCustomUserForm(request.POST)
        form.fields['password1'].required = True
        form.fields['password2'].required = True
        if form.is_valid():
            user = form.save(commit=False)
            user.username = form.cleaned_data["username"]
            user.create_by = request.user
            user.update_by = request.user
            user.set_password(form.cleaned_data["password1"])
            user.save()
            #messages.success(request, '歡迎註冊')
            return redirect('user_list')
        else:
            return render(request, template, {'userForm': form})


@login_required
def detail(request):
    template = 'users/edit.html'
    if request.method == 'POST':
        pk = request.POST.get('pk')
        member = CustomUser.objects.get(pk=pk)
        perm_pms = member.has_perm('users.perm_pms')
        perm_ams = member.has_perm('users.perm_ams')
        perm_workhour = member.has_perm('users.perm_workhour')
        perm_user_manage = member.has_perm('users.perm_user_manage')
        perm_misc_apply = member.has_perm('users.perm_misc_apply')
        perm_svr_monitor = member.has_perm('users.perm_svr_monitor')
        perm_stock = member.has_perm('users.perm_stock')

        if not request.user.is_superuser:
            form = CurrentCustomUserForm(instance=member, initial={'user_type': 2})
            form.fields["user_type"].queryset = UserType.objects.filter(type_name="一般使用者").all()
        else:
            form = CurrentCustomUserForm(instance=member)
        form.fields['emp_no'].widget.attrs['readonly'] = True

        return render(request, template, locals())

# Edit
@login_required
def user_edit(request):
    template = 'users/edit.html'
    if request.method == 'POST':
        pk = request.POST.get('pk')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        member = CustomUser.objects.get(pk=pk)
        form = CurrentCustomUserForm(request.POST, instance=member)

        if form.is_valid():
            user = form.save(commit=False)
            user.create_by = request.user
            user.update_by = request.user
            if password1 and password2:
                user.set_password(password1)
            user.save()
            return redirect('user_list')
    return render(request, template, locals())


# Edit
@login_required
def user_info(request):
    template = 'users/info.html'
    pk = request.user.pk
    member = CustomUser.objects.get(pk=pk)

    if request.method == 'POST':
        password = request.POST.get('password0')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        form = UserInfoForm(request.POST, instance=member)

        if form.is_valid():
            user = form.save(commit=False)
            user.update_by = request.user
            if password1 and password2:
                user.set_password(password1)
            user.save()
            messages.info(request, '修改成功!')
    else:
        form = UserInfoForm(instance=member)
    return render(request, template, locals())


@login_required
def user_list(request):
    template = 'users/list.html'

    user_keyword = ""

    query = Q(user_type__isnull=False)  # 排除超級管理者
    members = CustomUser.objects.filter(query)

    member_all = members.count()
    admin_count = members.filter(user_type=1, is_active=True).count()
    member_count = members.filter(user_type=2, is_active=True).count()

    if request.method == 'POST':
        user_keyword = request.POST.get('user_keyword')
        request.session['user_keyword'] = user_keyword

    if request.method == 'GET':
        if 'user_keyword' in request.session:
            user_keyword = request.session['user_keyword']

    if user_keyword:
        query.add(Q(emp_no__icontains=user_keyword), Q.AND)
        query.add(Q(first_name__icontains=user_keyword), Q.OR)
        query.add(Q(last_name__icontains=user_keyword), Q.OR)
        query.add(Q(username__icontains=user_keyword), Q.OR)
        query.add(Q(email__icontains=user_keyword), Q.OR)
        members = CustomUser.objects.filter(query)

    for member in members:
        if member.is_active:
            member.is_active_text = "啟用"
            member.is_active_color = "bg-success"
        else:
            member.is_active_text = "停用"
            member.is_active_color = "bg-danger"

        if member.last_login:
            member.last_login_color = "bg-light"
        else:
            member.last_login_color = "bg-secondary"

    return render(request, template, locals())

# Ajax API
@login_required
def user_auth_api(request):
    if request.method == 'POST':
        pk = request.POST.get('pk')

        user = CustomUser.objects.get(pk=pk)

        if request.POST.get('perm_pms'):
            add_permission(user, 'perm_pms')
        else:
            remove_permission(user, 'perm_pms')

        if request.POST.get('perm_ams'):
            add_permission(user, 'perm_ams')
        else:
            remove_permission(user, 'perm_ams')

        if request.POST.get('perm_workhour'):
            add_permission(user, 'perm_workhour')
        else:
            remove_permission(user, 'perm_workhour')

        if request.POST.get('perm_user_manage'):
            add_permission(user, 'perm_user_manage')
        else:
            remove_permission(user, 'perm_user_manage')

        if request.POST.get('perm_misc_apply'):
            add_permission(user, 'perm_misc_apply')
        else:
            remove_permission(user, 'perm_misc_apply')

        if request.POST.get('perm_svr_monitor'):
            add_permission(user, 'perm_svr_monitor')
        else:
            remove_permission(user, 'perm_svr_monitor')

        if request.POST.get('perm_stock'):
            add_permission(user, 'perm_stock')
        else:
            remove_permission(user, 'perm_stock')

        msg = "權限更新完成"
        return JsonResponse(msg, safe=False)


@login_required
def unit_list(request):
    template = 'users/unit_list.html'
    units = Unit.objects.all()
    return render(request, template, locals())


@login_required
def unit_sync(request):
    template = 'users/unit_list.html'

    if request.method == 'POST':
        sql = """SELECT OrganizationUnit.id AS unitId
                    ,Organization.id AS orgId
                    ,OrganizationUnit.organizationUnitName AS unitName
                    ,OrganizationUnit.organizationUnitType AS organizationUnitType
                    ,OrganizationUnitLevel.organizationUnitLevelName AS levelName
                    ,OrganizationUnit.validType AS isValid
                    ,Manager.id managerId
                    ,Manager.userName manager
                FROM OrganizationUnit
                INNER JOIN Organization ON OrganizationUnit.organizationOID = Organization.OID
                LEFT JOIN OrganizationUnitLevel ON OrganizationUnit.levelOID = OrganizationUnitLevel.OID
                LEFT JOIN Users Manager ON OrganizationUnit.managerOID = Manager.OID
                where OrganizationUnit.validType = 1
                ORDER BY unitId"""
        db = bpm_database()
        rows = db.select_sql_dict(sql)

        for row in rows:
            try:  # 更新
                if CustomUser.objects.filter(emp_no=row['managerId']).exists():
                    unit = Unit.objects.get(unitId=row['unitId'])
                    unit.unitName = row['unitName']
                    unit.manager = CustomUser.objects.get(emp_no=row['managerId'])
                    unit.isValid = row['isValid']
                    unit.update_by = request.user
                    unit.save()
                else:
                    print("{unitName} BPM尚未設定部門主管".format(unitName=row['unitName']))
            except:  # 新增
                unit = Unit(orgId=row['orgId'], unitId=row['unitId'], unitName=row['unitName'], isValid=row['isValid'])
                unit.manager = CustomUser.objects.get(emp_no=row['managerId'])
                unit.create_by = request.user
                unit.update_by = request.user
                unit.save()
        return redirect('unit_list')


@login_required
def user_sync(request):
    template = 'users/user_list.html'
    if request.method == 'POST':
        sql = """SELECT userId,main.userName,main.leaveDate,main.mailAddress,unitId,orgId,functionName,isMain,isnull(main.managerId,boss.id) managerId,levelName from (
                    SELECT Occupant.id AS userId
                                        ,Occupant.userName AS userName
                                        ,Occupant.leaveDate AS leaveDate
                                        ,Occupant.mailAddress
                                        ,OrganizationUnit.id AS unitId
                                        ,Organization.id AS orgId
                                        ,FunctionDefinition.functionDefinitionName AS functionName
                                        ,Functions.isMain AS isMain
                                        ,Manager.id AS managerId
                                        ,FunctionLevel.functionLevelName AS levelName
                                    FROM Functions
                                    INNER JOIN Users Occupant ON Functions.occupantOID = Occupant.OID
                                    INNER JOIN OrganizationUnit
                                    INNER JOIN Organization ON OrganizationUnit.organizationOID = Organization.OID ON Functions.organizationUnitOID = OrganizationUnit.OID INNER JOIN FunctionDefinition ON Functions.definitionOID = FunctionDefinition.OID LEFT JOIN FunctionLevel ON Functions.approvalLevelOID = FunctionLevel.OID LEFT JOIN Users Manager ON Functions.specifiedManagerOID = Manager.OID
                                    where isMain = 1 and OrganizationUnit.validType=1) main, OrganizationUnit unit, Users boss
                                    where main.unitId = unit.id and unit.managerOID = boss.OID
                                    order by userId"""
        db = bpm_database()
        rows = db.select_sql_dict(sql)

        for row in rows:
            try:
                # Noah有存在人員就更新資料
                if CustomUser.objects.filter(emp_no=row['userId']).exists():
                    user = CustomUser.objects.get(emp_no=row['userId'])
                    if row['leaveDate']:
                        user.is_active = False
                        user.save()
                    else:
                        user.unit = Unit.objects.get(unitId=row['unitId'])
                        if CustomUser.objects.filter(emp_no=row['managerId']).exists():
                            user.manager = CustomUser.objects.get(emp_no=row['managerId'])
                        user.update_by = request.user
                        user.email = row['mailAddress']
                        user.save()
                else:  # 不存在就新增
                    if not row['leaveDate']:
                        user = CustomUser(is_staff=1, is_active=1, user_type_id=2)
                        user.username = row['userName']
                        user.email = row['mailAddress']
                        user.emp_no = row['userId']
                        user.unit = Unit.objects.get(unitId=row['unitId'])
                        if CustomUser.objects.filter(emp_no=row['managerId']).exists():
                            user.manager = CustomUser.objects.get(emp_no=row['managerId'])
                        user.set_password(row['userId'])
                        user.create_by = request.user
                        user.update_by = request.user
                        user.save()
            except Exception as e:
                print(e)

        users = CustomUser.objects.filter(manager_id__isnull=True)
        for user in users:
            unit = Unit.objects.get(unitId=user.unit.unitId)
            user.manager = unit.manager
            user.create_by = request.user
            user.update_by = request.user
            user.save()
    return redirect('user_list')


def get_deptuser_api(request):
    if request.method == 'POST':
        unit = request.POST.get('unit')
        employees = CustomUser.objects.filter(unit=unit, is_active=True)
        html = """<option value="" selected>---------</option>"""

        for employee in employees:
            html += """<option value="{value}">{name}</option>""".format(value=employee.id, name=employee.username)
    return JsonResponse(html, safe=False)