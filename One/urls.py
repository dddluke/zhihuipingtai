from django.urls import path
from django.conf.urls import url
from django.urls import include
from .views import *
from rest_framework.authtoken import views
from rest_framework_jwt.views import obtain_jwt_token
from One import views

app_name = "one"

urlpatterns = [
    url(r'^test/', test.as_view()),
    # url(r'^test1/', test1.as_view()),
    url(r'^login1/', views.login1, name='login1'),
    url(r'^do_login/', views.do_login, name='do_login'),
    # 搜素功能
    url(r'^companylist/', Companylist.as_view()),  # 搜索所有激活状态公司
    url(r'^allcompanylist/', Allcompanylist.as_view()),  # 搜索所有激活状态公司
    # url(r'^unactivatedcompanylist/', views.unactivatedcompanylist),  # 搜索所有未激活状态公司
    url(r'^unactivatedcompanylist/', Unactivatedcompanylist.as_view()),  # 搜索所有未激活状态公司
    url(r'^userlist/', views.userlist),  # 查看所有激活状态用户
    url(r'^unactivateduserlist/', views.unactivateduserlist),  # 查看所有未激活状态用户

    # 用户CRUD
    url(r'^register/', RegisterView.as_view()),  # 注册
    url(r'^login/', LoginView.as_view()),  # 登录
    url(r'^blogin/', Login.as_view()),  # 后台登录
    url(r'^logout/', Logout.as_view()),  # 后台登录
    url(r'^index/', Order.as_view()),  # 未完成
    url(r'^api-jwt-auth/', obtain_jwt_token),  # jwt的认证接口（路径可自定义任意命名）
    url(r'^editmyprofile/', Editmyprofile.as_view()),  # 查看&&编辑个人信息，需登陆
    url(r'^changepassword/', Changepassword.as_view()),  # 修改密码，需登陆
    # 忘记密码 修改密码 未登录状态
    url(r'^forgetpassword/', ForgotPassword.as_view()),  # 忘记密码 修改密码 未登录状态
    url(r'^modifyphonenumber/', ModifyPhoneNumber.as_view()),  # 用户修改手机号

    # 公司CRUD
    url(r'^createcompany/', Createcompany.as_view()),  # 创建公司，需登陆
    url(r'^companyprofile/', Companyprofile.as_view()),  # 查看公司详情
    url(r'^editcompany/', Editcompany.as_view()),  # 查看自己的公司、编辑公司，需公司管理员操作(需要分开写
    url(r'^deactivecompany/', Deactivatecompany.as_view()),  # 停用公司
    url(r'^selectcompany/', SelectCompany.as_view()),  # 通过公司名字搜索公司

    # 员工与公司 CRUD
    url(r'^joincompany/', Joincompany.as_view()),  # 加入公司，需登陆
    url(r'^unactivestafflist/', Unactivestafflist.as_view()),  # 查看新员工申请，需公司管理员操作
    url(r'^enrollstaff/', Enrollstaff.as_view()),  # 公司添加员工，需公司管理员操作
    url(r'^deactivatestaff/', Deactivatestaff.as_view()),  # 公司停用员工，需公司管理员操作
    url(r'^companystaff/', Companystaff.as_view()),  # 查看公司员工（员工列表），需登陆
    url(r'^managercreatestaff/', ManagerCreateStaff.as_view()),  # 管理员创建员工

    # 项目与公司 CRUD
    url(r'^createproject/', Createproject.as_view()),  # 创建项目，需公司管理员操作
    url(r'^projectlist/', Projectlist.as_view()),  # 查看公司所有项目，需公司管理员或该公司员工
    url(r'^viewproject/', Viewproject.as_view()),  # 查看项目信息, 查看需为该公司员工
    url(r'^editproject/', Editproject.as_view()),  # 修改项目信息，修改需公司管理员操作
    url(r'^deactivateproject/', Deactivateproject.as_view()),  # 删除项目，需公司管理员操作

    # 项目、采集设备与员工 CRUD
    url(r'^signproject/', Signproject.as_view()),  # 关联用户和项目，需要公司管理员或后台人员身份
    url(r'^responserlist/', Responserlist.as_view()),  # 查看项目关联用户列表，需要公司管理员或后台人员身份
    url(r'^unsignproject/', Unsignproject.as_view()),  # 取消用户与项目关联，需要公司管理员或后台人员身份
    url(r'^collectdeviceattlistv3/', Collectdeviceattlistv3.as_view()),  # 设备管理员查看我的设备列表
    url(r'^devicelistv2/', Devicelistv2.as_view()),  # 设备管理员查看采集设备下数据信息

    # 通过采集设备查看项目组态图
    url(r'^dashboardv2/', Dashboardv2.as_view()),  # 通过nodeid查询项目组态图
    # 项目与设备 CRUD
    url(r'^applycollectdevice/', Applycollectdevice.as_view()),  # 在项目中添加采集设备，需公司管理员或运维人员操作

    url(r'^collectdevicelist/', Collectdevicelist.as_view()),  # 查看项目采集设备信息列表，需公司管理员或运维人员操作
    url(r'^collectdevicelistv2/', Collectdevicelistv2.as_view()),  # 查看公司采集设备列表
    url(r'^editcollectdevice/', Editcollectdevice.as_view()),  # 查看&修改采集设备信息，需公司管理员或运维人员操作
    url(r'^delcollectdevice/', Delcollectdevice.as_view()),  # 删除采集设备，需公司管理员或运维人员操作
    url(r'^collectdeviceatt/', Collectdeviceatt.as_view()),  # 添加采集设备属性，需公司管理员或运维人员操作
    # url(r'^viewcollectdeviceatt/', Viewcollectdeviceatt.as_view()),  # 查看采集设备属性，需公司管理员或运维人员操作
    url(r'^editcollectdeviceatt/', Editcollectdeviceatt.as_view()),  # 查看&修改采集设备属性，需公司管理员或运维人员操作
    url(r'^delcollectdeviceatt/', Delcollectdeviceatt.as_view()),  # 删除采集设备属性，需公司管理员或运维人员操作

    url(r'^applydevice/', Applydevice.as_view()),  # 在项目中添加设备，需公司管理员操作
    # url(r'^addlydeviceatt/', Adddeviceatt.as_view()),  # 添加机械设备属性，需公司管理员操作
    # url(r'^editdeviceatt/', Editdeviceatt.as_view()),  # 查看&修改机械设备属性，需公司管理员操作
    # url(r'^deldeviceatt/', Deldeviceatt.as_view()),  # 删除机械设备属性，需公司管理员操作
    url(r'^editdevice/', Editdevice.as_view()),  # 查看&&修改设备信息,需要公司管理员或设备负责人操作
    url(r'^devicelist/', Devicelist.as_view()),    # 查看项目设备列表
    # url(r'^viewdevicedata/', Viewdevicedata.as_view()),    # 查看设备全部数据（设备数据列表），实时告警，告警规则，历史告警都要做
    url(r'^signdevice/', Signdevice.as_view()),    # 关联设备与公司员工
    url(r'^unsigndevice/', Unsigndevice.as_view()),    # 取消设备与公司员工关联
    # url(r'^deactivedevice/', Unsigndevice.as_view()),    # 取消设备与公司员工关联
    # 机械设备属性
    url(r'^addlydeviceatt/', Adddeviceatt.as_view()),  # 添加机械设备属性，需公司管理员操作
    url(r'^editdeviceatt/', Editdeviceatt.as_view()),  # 查看&修改机械设备属性，需公司管理员操作
    url(r'^deldeviceatt/', Deldeviceatt.as_view()),  # 删除机械设备属性，需公司管理员操作

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
    url(r'^createusercomplain/', CreateUserComplain.as_view()),  # 客户创建投诉记录
    url(r'^deleteusercomplain/', DeleteUserComplain.as_view()),  # 客户删除投诉记录
    url(r'^selectmycomplain/', SelectMyComplain.as_view()),  # 客户查看自己投诉记录列表
    # url(r'selectmycomplain', SelectMyComplain.as_view({'get':'list'})),
    url(r'^selectcomplaindetail/', SelectComplainDetail.as_view()),  # 客户查看自己投诉记录详情
    url(r'^changemycomplain/', ChangeMyComplain.as_view()),  # 客户变更自己的投诉记录状态
    url(r'^selectemployeecomplain/', SelectEmployeeComplain.as_view()),  # 客服查看自己投诉记录列表
    url(r'^selectemployeecomplaindetail/', SelectEmployeeComplainDetail.as_view()),  # 客服查看自己投诉记录详情

    # 客服与客户历史投诉记录解决方案 CRUD
    # 客服查看自己未解决的投诉记录列表
    url(r'^selectemployeeunresolve/', SelectEmployeeUnresolve.as_view()),
    # 客服创建投诉记录解决方案
    # 客服查看自己的投诉记录解决方案
    # 客服编辑自己的投诉记录解决方案
    # 客户查看投诉记录解决方案

    # 审批新公司申请
    # 搜索所有未激活状态公司，之前已实现功能
    # 查看公司详情，之前已实现功能
    url(r'^activecompany/', Activatecompany.as_view()),  # 通过审批
    # 驳回审批，暂无必要实现 可能需要修改数据库

    # 新设备申请权限审批
    url(r'^deactivedevicelist/', Deactivedevicelist.as_view()),   # 搜索所有未激活状态的设备
    url(r'^activedevice/', Activatedevice.as_view()),  # 通过审核
    # 驳回审批，暂无法实现 可能需要修改数据库

    # 设备维修记录 CRUD
    url(r'^addmaintainrecord/', Addmaintainrecord.as_view()),  # 运维创建设备维修记录 or 设备负责人创建设备维修记录
    url(r'^maintainrecordlist/', Maintainrecordlist.as_view()),  # 查看设备所有维修记录
    url(r'^viewmaintainrecord/', ViewMaintainrecord.as_view()),  # 查看维修记录详情
    url(r'^deletemaintainrecord/', DeleteMaintainrecord.as_view()),  # 运维删除设备维修记录

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
    url(r'^editworksheet/', Editworksheet.as_view()),  # 查看工单详情&&编辑工单
    # url(r'^deleteworksheet/', Deleteworksheet.as_view()),  # 删除工单，可能不需要删除工单

    # 知识库与行业资讯 CRUD
    url(r'^addknowledge/', Addknowledge.as_view()),  # 运维添加知识库/行业资讯
    url(r'^addenterprise/', Addenterprise.as_view()),  # 运维添加企业动态
    url(r'^enterpriselist/', Enterpriselist.as_view()),  # 查询企业动态列表
    url(r'^viewenterprise/', Viewenterprise.as_view()),  # 查询企业动态列表详情&&编辑企业动态
    url(r'^deleteenterprise/', Deleteenterprise.as_view()),  # 删除企业动态
    url(r'^uploadimage/', Uploadimage.as_view()),  # 富文本编辑上传图片
    url(r'^knowledgelist/', Knowledgelist.as_view()),  # 查询知识库列表
    url(r'^knowledgelistv2/', KnowledgelistV2.as_view()),  # 查询行业资讯列表
    url(r'^knowledgelistv3/', KnowledgelistV3.as_view()),  # 根据标签查询行业资讯列表
    url(r'^knowledgelistv4/', KnowledgelistV4.as_view()),  # 查询最新的五条行业资讯
    url(r'^viewknowledge/', Viewknowledge.as_view()),  # 查询知识库/行业资讯详情&&编辑知识库/行业资讯
    url(r'^editknowledge/', Editknowledge.as_view()),  # 查询知识库/行业资讯详情&&编辑知识库/行业资讯
    url(r'^deleteknowledge/', Deleteknowledge.as_view()),  # 删除知识库/行业资讯

    # 知识库解决方案 CRUD
    url(r'^addsolution/', Addsolution.as_view()),  # 运维添加知识库/行业资讯解决方案
    url(r'^viewsolution/', Viewsolution.as_view()),  # 查看知识库/行业资讯解决方案&&编辑知识库/行业资讯解决方案
    url(r'^deletesolution/', Deletesolution.as_view()),  # 删除知识库/行业资讯解决方案

    # 平台管理
    # url(r'^editdamo', Editdamo.as_view()), # 编辑达摩企业信息，需要admin操作
    # url(r'^addemployee', Addemployee.as_view()), # 新增平台工作人员账号，需要admin操作
    # url(r'^adddepartment', Adddepartment.as_view()), # 新增平台部门，需要admin操作
    url(r'^employeelist', Employeelist.as_view()),  # 展示后台全部员工，需要admin操作
    url(r'^managercreatestaffv2/', ManagerCreateStaffv2.as_view()),  # 超级管理员创建后台员工
    url(r'^editstaff/', Editstaff.as_view()),  # 超级管理员编辑后台员工
    url(r'^staffcategory/', Staffcategory.as_view()),  # 按类型展示员工
    url(r'^deactivatestaffv2/', DeactivateStaffv2.as_view()),  # 停用后台员工
    # url(r'^wisepasstoken/', Wisepasstoken.as_view()),  # 查看当前研华token
    url(r'^wisepasstoken/', Wisepasstoken.as_view()),  # 查看当前研华token
    url(r'^editwisepasstoken/', Editwisepasstoken.as_view()),  # 更新研华token
]
