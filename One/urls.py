from django.urls import path
from django.conf.urls import url
from django.urls import include
from .views import *
from rest_framework.authtoken import views
from rest_framework_jwt.views import obtain_jwt_token
from One import views

app_name = "one"

urlpatterns = [

    # 搜素功能
    url(r'^companylist/', views.companylist),  # 搜索所有激活状态公司
    # url(r'^unactivatedcompanylist/', views.unactivatedcompanylist),  # 搜索所有未激活状态公司
    url(r'^unactivatedcompanylist/', Unactivatedcompanylist.as_view()),  # 搜索所有未激活状态公司
    url(r'^userlist/', views.userlist),  # 查看所有激活状态用户
    url(r'^unactivateduserlist/', views.unactivateduserlist),  # 查看所有未激活状态用户

    # 用户CRUD
    url(r'^sms/', SmsView.as_view()),  # 注册时手机号验证
    url(r'^smsvalid/', Smsvalid.as_view()),  # 修改密码时手机号验证
    url(r'^register/', RegisterView.as_view()),  # 注册
    url(r'^login/', LoginView.as_view()),  # 登录
    url(r'^index/', Order.as_view()),  # 未完成
    url(r'^api-jwt-auth/', obtain_jwt_token),  # jwt的认证接口（路径可自定义任意命名）
    url(r'^editmyprofile/', Editmyprofile.as_view()),  # 查看&&编辑个人信息，需登陆
    url(r'^changepassword/', Changepassword.as_view()),  # 修改密码，需登陆

    # 公司CRUD
    url(r'^createcompany/', Createcompany.as_view()),  # 创建公司，需登陆
    url(r'^companyprofile/', Companyprofile.as_view()),  # 查看公司详情
    url(r'^editcompany/', Editcompany.as_view()),  # 查看自己的公司、编辑公司，需公司管理员操作(需要分开写
    url(r'^deactivecompany/', Deactivatecompany.as_view()),  # 停用公司

    # 员工与公司 CRUD
    url(r'^joincompany/', Joincompany.as_view()),  # 加入公司，需登陆
    url(r'^enrollstaff/', Enrollstaff.as_view()),  # 公司添加员工，需公司管理员操作
    url(r'^deactivatestaff/', Deactivatestaff.as_view()),  # 公司停用员工，需公司管理员操作
    url(r'^companystaff/', Companystaff.as_view()),  # 查看公司员工（员工列表），需登陆

    # 项目与公司 CRUD
    url(r'^createproject/', Createproject.as_view()),  # 创建项目，需公司管理员操作
    url(r'^projectlist/', views.projectlist),  # 查看公司所有项目，需公司管理员或该公司员工
    url(r'^viewproject/', Viewproject.as_view()),  # 查看项目信息, 查看需为该公司员工
    url(r'^editproject/', Editproject.as_view()),  # 修改项目信息，修改需公司管理员操作
    url(r'^deactivateproject/', Deactivateproject.as_view()),  # 删除项目，需公司管理员操作

    # 项目与设备 CRUD
    url(r'^applydevice/', Applydevice.as_view()),  # 在项目中添加设备，需公司管理员操作
    url(r'^editdevice/', Editdevice.as_view()),  # 查看&&修改设备信息,需要公司管理员或设备负责人操作
    url(r'^devicelist/', Devicelist.as_view()),    # 查看项目设备列表
    # url(r'^viewdevicedata/', Viewdevicedata.as_view()),    # 查看设备全部数据（设备数据列表），实时告警，告警规则，历史告警都要做
    url(r'^signdevice/', Signdevice.as_view()),    # 关联设备与公司员工
    url(r'^unsigndevice/', Unsigndevice.as_view()),    # 取消设备与公司员工关联
    # url(r'^deactivedevice/', Unsigndevice.as_view()),    # 取消设备与公司员工关联

    # 设备与数据 CRUD
    url(r'^adddata/', Adddata.as_view()),  # 为设备添加数据
    url(r'^viewdata/', Viewdata.as_view()),  # 查看设备数据
    url(r'^deletedata/', Deletedata.as_view()),  # 删除设备数据
    # url(r'^datahistory', Datahistory.as_view()), # 查看设备数据历史 （暂无数据模型，无法实现

    # 数据与报警规则
    url(r'^addalert/', Addalert.as_view()),  # 为数据添加告警规则
    url(r'^viewalert/', Viewalert.as_view()),  # 查询数据告警规则
    url(r'^editalert/', Editalert.as_view()),  # 编辑数据告警规则
    url(r'^deletealert/', Deletealert.as_view()),  # 删除数据告警规则

    # 后台服务
    # 与客服聊天

    # 客服与客户历史投诉记录 CRUD
    # 客户创建投诉记录
    # 客户删除投诉记录
    # 客户查看自己投诉记录列表
    # 客户查看自己投诉记录详情
    # 客户编辑自己的投诉记录
    # 客服查看自己投诉记录列表
    # 客服查看自己投诉记录详情
    # 客户变更投诉记录为已解决

    # 客服与客户历史投诉记录解决方案 CRUD
    # 客服查看自己未解决的投诉记录列表
    # 客服创建投诉记录解决方案
    # 客服查看自己的投诉记录解决方案
    # 客服编辑自己的投诉记录解决方案
    # 客户查看投诉记录解决方案

    # 审批新公司申请
    # 搜索所有未激活状态公司，之前已实现功能
    # 查看公司详情，之前已实现功能
    url(r'^activecompany/', Activatecompany.as_view()),  # 通过审批
    # 驳回审批，暂无法实现 可能需要修改数据库

    # 新设备申请权限审批
    url(r'^deactivedevicelist/', Deactivedevicelist.as_view()),   # 搜索所有未激活状态的设备
    url(r'^activedevice/', Activatedevice.as_view()),  # 通过审核
    # 驳回审批，暂无法实现 可能需要修改数据库

    # 设备维修记录 CRUD
    # 运维创建设备维修记录 or 设备负责人创建设备维修记录
    # 查看设备所有维修记录
    # 查看维修记录详情
    # 运维删除设备维修记录

    # 报表管理  上传下载
    # 上传excel格式文件
    # 查看报表列表
    # 搜索报表列表（可通过查询公司名，编辑人名等搜索）
    # 预览报表
    # 下载报表

    # 工单 CRUD
    url(r'^addworksheet/', Addworksheet.as_view()),  # 添加工单
    url(r'^viewworksheets/', Viewworksheets.as_view()),  # 查看全部工单列表
    url(r'^viewmyworksheets/', Viewmyworksheets.as_view()),  # 查看我的工单
    url(r'^searchworksheets/', Searchworksheets.as_view()),  # 搜索工单（根据名称、时间段） 需修改
    # url(r'^editworksheet/', Editworksheet.as_view()),  # 查看工单详情&&编辑工单
    # url(r'^deleteworksheet/', Deleteworksheet.as_view()),  # 删除工单，可能不需要删除工单

    # 知识库与行业资讯 CRUD
    # 运维添加知识库/行业资讯
    # 查询知识库列表
    # 查询行业资讯列表
    # 查询知识库/行业资讯详情&&编辑知识库/行业资讯
    # 删除知识库/行业资讯

    # 知识库与行业资讯解决方案 CRUD
    # 运维添加知识库/行业资讯解决方案
    # 查看知识库/行业资讯解决方案&&编辑知识库/行业资讯解决方案
    # 删除知识库/行业资讯解决方案

    # 平台管理
    # url(r'^editdamo', Editdamo.as_view()), # 编辑达摩企业信息，需要admin操作
    # url(r'^addemployee', Addemployee.as_view()), # 新增平台工作人员账号，需要admin操作
    # url(r'^adddepartment', Adddepartment.as_view()), # 新增平台部门，需要admin操作


]
