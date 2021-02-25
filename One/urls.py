from django.conf.urls import url
from rest_framework_jwt.views import obtain_jwt_token

from One import views
from .views import *

app_name = "one"

urlpatterns = [
    # --------------------------------------------------------------------------------------------------------
    # 测试
    # --------------------------------------------------------------------------------------------------------
    url(r'^test/', test.as_view()),
    # url(r'^login1/', views.login1, name='login1'),
    url(r'^do_login/', views.do_login, name='do_login'),
    url(r'^historydata/', views.historydata),  # 小程序折线图按设备查询
    url(r'^deletedata/', views.deletedata),  # 小程序折线图按设备查询
    url(r'^uniontest/', views.uniontest),  # 小程序折线图按设备查询
    url(r'^qrcode/', views.qrcode),  # 微信扫码登录
    url(r'^qrcodev1/', views.qrcodev1),  # 微信扫码绑定
    url(r'^qrcodev2/', views.qrcodev2),  # 微信扫码绑定
    # --------------------------------------------------------------------------------------------------------
    # 搜素功能
    # --------------------------------------------------------------------------------------------------------
    url(r'^companylist/', Companylist.as_view()),  # 搜索所有激活状态公司
    url(r'^allcompanylist/', Allcompanylist.as_view()),  # 搜索所有公司
    url(r'^unactivatedcompanylist/', Unactivatedcompanylist.as_view()),  # 搜索所有未激活状态公司
    # url(r'^userlist/', views.userlist),  # 查看所有激活状态用户
    # url(r'^unactivateduserlist/', views.unactivateduserlist),  # 查看所有未激活状态用户

    # --------------------------------------------------------------------------------------------------------
    # 用户CRUD
    # --------------------------------------------------------------------------------------------------------
    url(r'^register/', RegisterView.as_view()),  # 注册
    url(r'^useraddtags/', UserAddTags.as_view()),  # 用户添加标签
    url(r'^usertags/', UserTags.as_view()),  # 用户查看标签
    url(r'^useredittags/', UserEditTags.as_view()),  # 用户编辑标签
    url(r'^login/', LoginView.as_view()),  # 登录
    url(r'^blogin/', Login.as_view()),  # 后台登录
    url(r'^logout/', Logout.as_view()),  # 后台登出
    url(r'^api-jwt-auth/', obtain_jwt_token),  # jwt的认证接口（路径可自定义任意命名）
    url(r'^editmyprofile/', Editmyprofile.as_view()),  # 查看&&编辑个人信息，需登陆
    url(r'^changepassword/', Changepassword.as_view()),  # 修改密码，需登陆

    # --------------------------------------------------------------------------------------------------------
    # 忘记密码 修改密码 未登录状态
    # --------------------------------------------------------------------------------------------------------
    url(r'^forgetpassword/', ForgotPassword.as_view()),  # 忘记密码 修改密码 未登录状态
    url(r'^modifyphonenumber/', ModifyPhoneNumber.as_view()),  # 用户修改手机号

    # --------------------------------------------------------------------------------------------------------
    # 公司CRUD
    # --------------------------------------------------------------------------------------------------------
    url(r'^createcompany/', Createcompany.as_view()),  # 创建公司，需登陆
    url(r'^createdraftcompany/', CreateDraftcompany.as_view()),  # 创建公司，需登陆
    url(r'^companyprofile/', Companyprofile.as_view()),  # 查看公司详情
    url(r'^editcompany/', Editcompany.as_view()),  # 查看自己的公司、编辑公司，需公司管理员操作(需要分开写
    url(r'^editdraftcompany/', EditDraftcompany.as_view()),  # 查看自己的公司、编辑公司，需公司管理员操作(需要分开写
    url(r'^deactivecompany/', Deactivatecompany.as_view()),  # 停用公司
    url(r'^selectcompany/', SelectCompany.as_view()),  # 通过公司名字搜索公司

    # --------------------------------------------------------------------------------------------------------
    # 员工与公司 CRUD
    # --------------------------------------------------------------------------------------------------------
    url(r'^joincompany/', Joincompany.as_view()),  # 加入公司，需登陆
    url(r'^unactivestafflist/', Unactivestafflist.as_view()),  # 查看新员工申请，需公司管理员操作
    url(r'^enrollstaff/', Enrollstaff.as_view()),  # 公司添加员工，需公司管理员操作
    url(r'^deactivatestaff/', Deactivatestaff.as_view()),  # 公司停用员工，需公司管理员操作
    url(r'^companystaff/', Companystaff.as_view()),  # 查看公司员工（员工列表），需登陆
    url(r'^managercreatestaff/', ManagerCreateStaff.as_view()),  # 管理员创建员工
    url(r'^managerchangestaffwork/', MCSwork.as_view()),  # 管理员更改用户身份

    # --------------------------------------------------------------------------------------------------------
    # 项目与公司 CRUD
    # --------------------------------------------------------------------------------------------------------
    url(r'^createproject/', Createproject.as_view()),  # 创建项目，需公司管理员操作
    url(r'^projectlist/', Projectlist.as_view()),  # 查看公司所有项目，需公司管理员或该公司员工
    url(r'^viewproject/', Viewproject.as_view()),  # 查看项目信息, 查看需为该公司员工
    url(r'^editproject/', Editproject.as_view()),  # 修改项目信息，修改需公司管理员操作
    url(r'^deactivateproject/', Deactivateproject.as_view()),  # 删除项目，需公司管理员操作

    # --------------------------------------------------------------------------------------------------------
    # 项目、采集设备与员工 CRUD
    # --------------------------------------------------------------------------------------------------------
    url(r'^signproject/', Signproject.as_view()),  # 关联用户和项目，需要公司管理员或后台人员身份
    url(r'^responserlist/', Responserlist.as_view()),  # 查看项目关联用户列表，需要公司管理员或后台人员身份
    url(r'^unsignproject/', Unsignproject.as_view()),  # 取消用户与项目关联，需要公司管理员或后台人员身份
    url(r'^collectdeviceattlistv3/', Collectdeviceattlistv3.as_view()),  # 已弃用 设备管理员查看我的设备列表
    url(r'^devicelistv2/', Devicelistv2.as_view()),  # 设备管理员查看采集设备下数据信息

    # 通过采集设备查看项目组态图
    url(r'^dashboardv2/', Dashboardv2.as_view()),  # 通过nodeid查询项目组态图

    # --------------------------------------------------------------------------------------------------------
    # 项目与采集设备设备 CRUD
    # --------------------------------------------------------------------------------------------------------
    url(r'^applycollectdevice/', Applycollectdevice.as_view()),  # 已启用 在项目中添加采集设备，需公司管理员或运维人员操作
    url(r'^collectdevicelist/', Collectdevicelist.as_view()),  # 已启用 查看项目采集设备信息列表，需公司管理员或运维人员操作
    url(r'^collectdevicelistv2/', Collectdevicelistv2.as_view()),  # 查看公司采集设备列表/wisepass
    url(r'^editcollectdevice/', Editcollectdevice.as_view()),  # 已启用 查看&修改采集设备信息，需公司管理员或运维人员操作
    url(r'^delcollectdevice/', Delcollectdevice.as_view()),  # 已启用 删除采集设备，需公司管理员或运维人员操作

    # --------------------------------------------------------------------------------------------------------
    # 采集设备属性 CRUD
    # --------------------------------------------------------------------------------------------------------
    # url(r'^collectdeviceatt/', Collectdeviceatt.as_view()),  # 添加采集设备属性，需公司管理员或运维人员操作
    # # url(r'^viewcollectdeviceatt/', Viewcollectdeviceatt.as_view()),  # 查看采集设备属性，需公司管理员或运维人员操作
    # url(r'^editcollectdeviceatt/', Editcollectdeviceatt.as_view()),  # 查看&修改采集设备属性，需公司管理员或运维人员操作
    # url(r'^delcollectdeviceatt/', Delcollectdeviceatt.as_view()),  # 删除采集设备属性，需公司管理员或运维人员操作

    # --------------------------------------------------------------------------------------------------------
    # 项目与机械设备 CRUD
    # --------------------------------------------------------------------------------------------------------
    url(r'^applydevice/', Applydevice.as_view()),  # 已启用 在项目中添加设备，需公司管理员操作
    url(r'^editdevice/', Editdevice.as_view()),  # 查看&&修改设备信息,需要公司管理员或设备负责人操作
    url(r'^viewdevice/', viewdevice.as_view()),  # 查看&&修改设备信息,需要公司管理员或设备负责人操作
    url(r'^devicelist/', Devicelist.as_view()),  # 已启用 查看项目设备列表
    url(r'^persondevicelist/', PersonDevicelist.as_view()),  # 已启用 查看用户设备列表
    url(r'^deletedevice/', DeleteDevice.as_view()),  # 已启用 删除机械设备
    url(r'^signdevice/', Signdevice.as_view()),  # 关联设备与公司员工
    url(r'^unsigndevice/', Unsigndevice.as_view()),  # 取消设备与公司员工关联

    # --------------------------------------------------------------------------------------------------------
    # 机械设备属性 CRUD
    # --------------------------------------------------------------------------------------------------------
    url(r'^addlydeviceatt/', Adddeviceatt.as_view()),  # 已启用 添加机械设备属性，需公司管理员操作
    # url(r'^editdeviceatt/', Editdeviceatt.as_view()),  # 查看&修改机械设备属性，需公司管理员操作
    url(r'^deldeviceatt/', Deldeviceatt.as_view()),  # 已启用 删除机械设备属性，需公司管理员操作
    url(r'^devicegrouplist/', DeviceGrouplist.as_view()),  # 已启用 机械设备组列表
    url(r'^adddevicegroup/', AdddeviceGroup.as_view()),  # 已启用 添加机械组，需公司管理员、后台人员操作
    url(r'^deldevicegroup/', DeldeviceGroup.as_view()),  # 已启用 删除机械组，需公司管理员、后台人员操作

    # --------------------------------------------------------------------------------------------------------
    # 设备与数据 CRUD
    # --------------------------------------------------------------------------------------------------------
    # url(r'^adddata/', Adddata.as_view()),  # 为设备添加数据
    url(r'^viewdata/', Viewdata.as_view()),  # 查看采集设备参数列表
    url(r'^deviceadddata/', DeviceAddData.as_view()),  # 机械设备组添加参数
    url(r'^searchdata/', SearchData.as_view()),  # 搜索参数
    url(r'^deletedata/', Deletedata.as_view()),  # 删除设备数据
    # url(r'^datahistory', Datahistory.as_view()), # 查看设备数据历史 （暂无数据模型，无法实现

    # --------------------------------------------------------------------------------------------------------
    # 数据与报警规则
    # --------------------------------------------------------------------------------------------------------
    url(r'^addalert/', Addalert.as_view()),  # 为数据添加告警规则
    url(r'^editalert/', Editalert.as_view()),  # 查看&编辑数据告警规则
    url(r'^deletealert/', Deletealert.as_view()),  # 删除数据告警规则
    url(r'^alarmloglist/', AlarmLogList.as_view()),  # 告警记录
    url(r'^searchalarmlog/', SearchAlarmLog.as_view()),  # 告警记录
    url(r'^solvealarm/', SolveAlarm.as_view()),  # 解决告警

    # --------------------------------------------------------------------------------------------------------
    # 客服与客户历史投诉记录 CRUD
    # --------------------------------------------------------------------------------------------------------
    url(r'^createusercomplain/', CreateUserComplain.as_view()),  # 客户创建投诉记录
    url(r'^deleteusercomplain/', DeleteUserComplain.as_view()),  # 客户删除投诉记录
    url(r'^selectmycomplain/', SelectMyComplain.as_view()),  # 客户查看自己投诉记录列表
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
    # 驳回审批，暂无必要实现 可能需要修改数据库

    # --------------------------------------------------------------------------------------------------------
    # 设备维修记录 CRUD
    # --------------------------------------------------------------------------------------------------------
    url(r'^addmaintainrecord/', Addmaintainrecord.as_view()),  # 已启用 运维创建设备维修记录 or 设备负责人创建设备维修记录
    url(r'^maintainrecordlist/', Maintainrecordlist.as_view()),  # 已启用 查看设备所有维修记录
    url(r'^companymaintainrecordlist/', CompanyMaintainrecordlist.as_view()),  # 已启用 查看公司所有维修记录
    url(r'^companymaintainrecordlistv1/', CompanyMaintainrecordlistV1.as_view()),  # 已启用 查看设备所有维修记录
    url(r'^viewmaintainrecord/', ViewMaintainrecord.as_view()),  # 已启用 查看维修记录详情
    url(r'^deletemaintainrecord/', DeleteMaintainrecord.as_view()),  # 已启用 运维删除设备维修记录
    url(r'^searchrecords/', SearchRecords.as_view()),  # `已启用 搜素设备维修记录
    url(r'^searchrecordsv1/', SearchRecordsV1.as_view()),  # `已启用 小程序搜素设备维修记录

    # 报表管理  上传下载
    # 上传excel格式文件
    # 查看报表列表
    # 搜索报表列表（可通过查询公司名，编辑人名等搜索）
    # 预览报表
    # 下载报表

    # --------------------------------------------------------------------------------------------------------
    # 工单 CRUD
    # --------------------------------------------------------------------------------------------------------
    url(r'^addworksheet/', Addworksheet.as_view()),  # 添加工单
    url(r'^addworksheetdraft/', AddworksheetDraft.as_view()),  # 添加工单
    url(r'^createworksheet/', Createworksheet.as_view()),  # 微信添加工单
    url(r'^viewworksheets/', Viewworksheets.as_view()),  # 查看全部工单列表
    url(r'^searchworksheetsv1/', SearchworksheetsV1.as_view()),  # 查看全部工单列表
    url(r'^viewmyworksheets/', Viewmyworksheets.as_view()),  # 查看我的工单
    url(r'^searchworksheets/', Searchworksheets.as_view()),  # 搜索工单（根据名称、时间段） 需修改
    url(r'^editworksheet/', Editworksheet.as_view()),  # 查看工单详情&&编辑工单
    # url(r'^deleteworksheet/', Deleteworksheet.as_view()),  # 删除工单，可能不需要删除工单
    # 技术方案
    url(r'^viewdoc/', views.viewdoc),  # 在线预览技术方案
    url(r'^uploadtech/', Uploadtech.as_view()),  # 上传技术方案
    url(r'^deletetech/', Deletetech.as_view()),  # 删除技术方案
    url(r'^unactivetechlist/', Unactivetechlist.as_view()),  # 未激活技术方案列表
    url(r'^activetech/', Activetech.as_view()),  # 审核技术方案

    # --------------------------------------------------------------------------------------------------------
    # 知识库与行业资讯 CRUD
    # --------------------------------------------------------------------------------------------------------
    url(r'^addknowledge/', Addknowledge.as_view()),  # 运维添加知识库/行业资讯
    url(r'^addknowledgedraft/', AddknowledgeDraft.as_view()),  # 运维添加知识库/行业资讯
    url(r'^addenterprise/', Addenterprise.as_view()),  # 运维添加企业动态
    url(r'^enterpriselist/', Enterpriselist.as_view()),  # 查询企业动态列表
    url(r'^viewenterprise/', Viewenterprise.as_view()),  # 查询企业动态列表详情&&编辑企业动态
    url(r'^deleteenterprise/', Deleteenterprise.as_view()),  # 删除企业动态
    url(r'^uploadimage/', Uploadimage.as_view()),  # 富文本编辑上传图片
    url(r'^knowledgelist/', Knowledgelist.as_view()),  # 查询知识库列表 3
    url(r'^myknowledgelist/', MyKnowledgelist.as_view()),  # 查询知识库列表 3
    url(r'^myknowledgedraftlist/', MyKnowledgeDraftlist.as_view()),  # 查询知识库列表 3
    url(r'^knowledgelistv2/', KnowledgelistV2.as_view()),  # 查询行业资讯列表 3
    url(r'^myknowledgelistv1/', MyKnowledgelistV1.as_view()),  # 查询行业资讯列表 3
    url(r'^myknowledgedraftlistv1/', MyKnowledgeDraftlistV1.as_view()),  # 查询行业资讯列表 3
    url(r'^knowledgelistv3/', KnowledgelistV3.as_view()),  # 根据标签查询行业资讯列表 3
    url(r'^knowledgelistv4/', KnowledgelistV4.as_view()),  # 查询最新的五条行业资讯 3
    url(r'^knowledgelistv5/', KnowledgelistV5.as_view()),  # 查询最新的五条知识库 3
    url(r'^selectknoledgev1/', Selectknoledgev1.as_view()),  # 搜索知识库 3
    url(r'^selectknoledgev2/', Selectknoledgev2.as_view()),  # 搜索行业资讯 3
    url(r'^knowledgelistfront/', KnowledgelistFront.as_view()),  # 查询知识库列表  1 前台 3
    url(r'^knowledgelistv2front/', KnowledgelistV2Front.as_view()),  # 查询行业资讯列表   1  前台 3
    url(r'^viewknowledge/', Viewknowledge.as_view()),  # 查询知识库/行业资讯详情&&编辑知识库/行业资讯3
    url(r'^viewknowledge1/', Viewknowledge1.as_view()),  # 查询知识库/行业资讯详情&&编辑知识库/行业资讯3
    url(r'^kaddtag/', KAddTag.as_view()),  # 给知识库加标签
    url(r'^userknowlegematchbytags/', UKMactchTag.as_view()),  # 用户和知识库通过标签匹配 返回用户的知识库信息3
    # url(r'^knowlegelistv5/', UKMactchTag.as_view()),  # 用户和知识库通过标签匹配 返回用户的知识库信息
    url(r'^userknowlegematchbytags2/', UKMactchTag2.as_view()),  # 用户和行业资讯通过标签匹配 返回与用户匹配的行业资讯3
    url(r'^collectknowledge/', Collectknowledge.as_view()),  # 收藏知识库/行业资讯
    url(r'^uncollectknowledge/', UnCollectknowledge.as_view()),  # 取消收藏知识库/行业资讯
    url(r'^viewcollection/', ViewCollection.as_view()),  # 收藏知识库/行业资讯
    url(r'^thumbsknowledge/', Thumbknowledge.as_view()),  # 点赞知识库/行业资讯
    url(r'^editknowledge/', Editknowledge.as_view()),  # 查询知识库/行业资讯详情&&编辑知识库/行业资讯
    url(r'^deleteknowledge/', Deleteknowledge.as_view()),  # 删除知识库/行业资讯
    url(r'^verify/', Verfiy.as_view()),  # 审核知识库/行业资讯

    # 知识库解决方案 CRUD
    url(r'^addsolution/', Addsolution.as_view()),  # 运维添加知识库/行业资讯解决方案
    url(r'^viewsolution/', Viewsolution.as_view()),  # 查看知识库/行业资讯解决方案&&编辑知识库/行业资讯解决方案
    url(r'^deletesolution/', Deletesolution.as_view()),  # 删除知识库/行业资讯解决方案

    # --------------------------------------------------------------------------------------------------------
    # 平台管理
    # --------------------------------------------------------------------------------------------------------
    # url(r'^editdamo', Editdamo.as_view()), # 编辑达摩企业信息，需要admin操作
    # url(r'^addemployee', Addemployee.as_view()), # 新增平台工作人员账号，需要admin操作
    # url(r'^adddepartment', Adddepartment.as_view()), # 新增平台部门，需要admin操作

    url(r'^activecompany/', Activatecompany.as_view()),  # 新公司通过审批
    # 新设备申请权限审批
    url(r'^deactivedevicelist/', Deactivedevicelist.as_view()),  # 搜索所有未激活状态的设备
    url(r'^activedevice/', Activatedevice.as_view()),  # 通过审核

    url(r'^employeelist', Employeelist.as_view()),  # 展示后台全部员工，需要admin操作
    url(r'^managercreatestaffv2/', ManagerCreateStaffv2.as_view()),  # 超级管理员创建后台员工
    url(r'^managercreatestaffv3/', ManagerCreateStaffV3.as_view()),  # 超级管理员创建公司管理员
    url(r'^getnoneuser/', views.getnoneuser),  # 超级管理员查看待新建公司的用户
    url(r'^managercreatecompany/', ManagerCreateCompany.as_view()),  # 超级管理员创建公司
    url(r'^editstaff/', Editstaff.as_view()),  # 超级管理员编辑后台员工
    url(r'^staffcategory/', Staffcategory.as_view()),  # 按类型展示员工
    url(r'^deactivatestaffv2/', DeactivateStaffv2.as_view()),  # 停用后台员工
    url(r'^wisepasstoken/', Wisepasstoken.as_view()),  # 查看当前研华token
    # url(r'^editwisepasstoken/', Editwisepasstoken.as_view()),  # 更新研华token
    # url(r'^editwisepasstoken/', Editwisepasstoken.as_view()),  # 更新研华token

    # --------------------------------------------------------------------------------------------------------
    # 配件模块url
    # --------------------------------------------------------------------------------------------------------
    url(r'^addfittings/', AddFittings.as_view()),  # 添加配件
    url(r'^changefittings/', ChangeFittings.as_view()),  # 修改配件信息
    url(r'^deletefittings/', DeleteFittings.as_view()),  # 删除配件
    url(r'^selectfittings/', SelectFittings.as_view()),  # 查询配件信息
    url(r'^selectfitacsub/', SelectFitAccSub.as_view()),  # 根据类查询配件信息
    url(r'^addfitsub/', AddFitSub.as_view()),  # 添加配件类 1
    url(r'^selectfitsub/', SelectFitSub.as_view()),  # 查询配件类 1
    url(r'^deletefitsub/', DeleteFitSub.as_view()),  # 删除配件类
    url(r'^selectallfit/', SelectAllFit.as_view()),  # 返回所有配件类及配件信息
    url(r'^fixfitsub/', FixFitSub.as_view()),  # 修改配件类信息
    url(r'^selectabovefit/', SelectAboveFit.as_view()),  # 模糊查询配件

    # 默认图片库
    url(r'^uploaddefault/', uploaddefault.as_view()),  # 为项目导入采集设备数据

    # --------------------------------------------------------------------------------------------------------
    # 设备控制台相关
    # --------------------------------------------------------------------------------------------------------
    url(r'^devicestatus/', DeviceStatus.as_view()),  # 正常设备，异常设备
    url(r'^healthdevicelist/', HealthDeviceList.as_view()),  # 正常设备
    url(r'^unhealthdevicelist/', UnHealthDeviceList.as_view()),  # 异常设备
    # --------------------------------------------------------------------------------------------------------
    # Webaccess相关
    # --------------------------------------------------------------------------------------------------------
    url(r'^getdevice/', views.getdevice),  # 为项目导入采集设备数据
    url(r'^gettags/', views.gettags),  # 为项目导入采集设备数据
    url(r'^threeinone3/', views.threeinone3),  # 获取某设备实时数据
    url(r'^threeinone2/', views.threeinone2),  # 三取一
    url(r'^threeinone/', views.threeinone),  # 三取一
    url(r'^oneweek/', views.oneweek),  # 最近一周历史数据
    url(r'^onemonth/', views.onemonth),  # 最近一月历史数据
    url(r'^yestaday/', views.yestaday),  # 昨日数据
    # url(r'^threeinone2/', views.threeinone2),  # 三取一
    # url(r'^testtttt/', views.testtttt),  # 三取一
    url(r'^testtttt/', views.testtttt),  # 最近24小时历史数据
    url(r'^wechatline/', views.wechatline),  # 小程序折线图默认界面
    url(r'^wechatlinev1/', views.wechatlinev1),  # 小程序折线图按设备查询
    url(r'^devicehealth/', views.devicehealth),  # 小程序设备健康数据按设备查询 默认页面
    url(r'^devicehealthv1/', views.devicehealthv1),  # 小程序设备健康数据按设备查询 选择设备后页面
    url(r'^devicealarmlogs/', views.devicealarmlogs),  # 小程序折线图按设备查询
    # url(r'^uploaddefault/', Uploaddefault.as_view()),  # 三取一

    # --------------------------------------------------------------------------------------------------------
    # 联系我们
    # --------------------------------------------------------------------------------------------------------
    url(r'^leavecontactmessage/', LeaveContactMessage.as_view()),  # 留言
    url(r'^contactmessagelist/', ContactMessageList.as_view()),  # 后台留言列表
    url(r'^viewcontactmessage/', ViewContactMessage.as_view()),  # 留言详细信息
    # --------------------------------------------------------------------------------------------------------
    # 小程序登录
    # --------------------------------------------------------------------------------------------------------
    url(r'^wechatlogin/', WechatLogin.as_view()),  # 小程序账号登录
    url(r'^wechatloginv2/', WechatLoginV2.as_view()),  # 小程序手机验证码登录
    # 小程序公司
    # 小程序公司
    url(r'^companyprolist/', CompanyProList.as_view()),  # 公司项目列表
    url(r'^companyprolistv1/', CompanyProListV1.as_view()),  # 公司项目列表
    # 小程序用户
    url(r'^changeicon/', ChangeIcon.as_view()),  # 小程序更换头像
    # 小程序设备
    url(r'^searchdevice/', SearchDevice.as_view()),  # 前台 搜素机械设备
    url(r'^searchdevicev1/', SearchDeviceV1.as_view()),  # 后台 搜素机械设备
    url(r'^persondevicelistv1/', PersonDevicelistV1.as_view()),  # 已启用 查看用户设备列表
    url(r'^persondevicelistv2/', PersonDevicelistV2.as_view()),  # 已启用 查看用户设备列表
    # 小程序工单
    url(r'^createworksheet/', Createworksheet.as_view()),  # 微信添加工单
    # 小程序知识库&行业资讯
    url(r'^viewcollectionv1/', ViewCollectionV1.as_view()),  # 知识库/行业资讯收藏夹
    url(r'^selectknoledgev3/', Selectknoledgev3.as_view()),  # 小程序查询最热的三条知识库 3
    url(r'^selectknoledgev4/', Selectknoledgev4.as_view()),  # 小程序查询最热的三条行业资讯 3
    url(r'^selectknoledgev5/', Selectknoledgev5.as_view()),  # 小程序查询知识库列表 3

    # --------------------------------------------------------------------------------------------------------
    # 大屏
    # --------------------------------------------------------------------------------------------------------
    url(r'^companycontrol/', CompanyControl.as_view()),  # 大屏左屏控制台数据统计
    url(r'^monthalarm/', MonthAlarm.as_view()),  # 大屏左屏设备月度报警统计
    url(r'^yearalarm/', YearAlarm.as_view()),  # 大屏左屏设备年度报警统计
    url(r'^alarmlist/', AlarmList.as_view()),  # 大屏左屏历史报警记录

    # 公告提醒
    # 建立 发送公告提醒 站内消息
    url(r'^sendannouncement/', SendAnnouncement.as_view()),  # 后台人员建立公告或者前台人员提醒 发送公告或者提醒
    # 展示公告信息
    url(r'^selectannounce/', SelectAnnounce.as_view()),  # 任意身份查询单个公告
    url(r'^selectallannounce/', SelectAllAnnounce.as_view()),  # 前台用户查询所有已发送的公告
    url(r'^aselectallannounce', ASelectAllAnnounce.as_view()),  # 超级管理员，运维查询所有的系统通知 即已发布的系统通知 可关键字查询

    url(r'^deleteannounce/', DeleteAnnounce.as_view()),  # 任意用户删除删除属于自己的单个公告
    # url(r'^deleteallannounce/', DeleteAllAnnounce.as_view()),  # 任意用户删除属于自己的所有公告消息
    # url(r'^readallmessage/', ReadAllMessage.as_view()),         # 普通用户一键已读所有公告
    url(r'^selectpremessage/', SelectPreMessage.as_view()),  # 前台查询未到时提醒通知 可添加关键字查询
    url(r'^closeoropenmessage/', AboutMessage.as_view()),  # 前台开启或者关闭定时任务
    # url(r'^fuserdeletemessage/', FUserDeleteMessage.as_view()),    # 完成前台用户删除自己到期的提醒
    url(r'^editmessage/', EditMessage.as_view()),  # 完成所有人更改自己发出的提醒公告
    url(r'^selectmessagealone/', SelectMessageAlone.as_view()),  # 所有人根据不同传参 查询到时保养提醒 系统公告


]
