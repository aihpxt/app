<template>
  <div class="admin-page">
    <div class="page-header">
      <div class="container">
        <h1 class="page-title">后台管理</h1>
        <p class="page-desc">管理系统用户、学校、政策等数据</p>
      </div>
    </div>

    <div class="container">
      <el-row :gutter="20">
        <el-col :xs="24" :md="8">
          <div class="menu-card card">
            <div class="section-title">
              <el-icon><Menu /></el-icon>
              <span>管理菜单</span>
            </div>
            <el-menu :default-active="activeMenu" class="admin-menu">
              <el-menu-item index="users" @click="activeMenu = 'users'">
                <el-icon><User /></el-icon>
                <span>用户管理</span>
              </el-menu-item>
              <el-menu-item index="schools" @click="activeMenu = 'schools'">
                <el-icon><OfficeBuilding /></el-icon>
                <span>学校管理</span>
              </el-menu-item>
              <el-menu-item index="policies" @click="activeMenu = 'policies'">
                <el-icon><Document /></el-icon>
                <span>政策管理</span>
              </el-menu-item>
              <el-menu-item index="students" @click="activeMenu = 'students'">
                <el-icon><Reading /></el-icon>
                <span>学生管理</span>
              </el-menu-item>
            </el-menu>
          </div>
        </el-col>

        <el-col :xs="24" :md="16">
          <!-- 用户管理 -->
          <div v-if="activeMenu === 'users'" class="content-card card">
            <div class="section-title">
              <el-icon><User /></el-icon>
              <span>用户管理</span>
            </div>
            <div class="admin-actions">
              <el-button type="primary" @click="dialogVisible = true">
                <el-icon><Plus /></el-icon>添加用户
              </el-button>
            </div>
            <el-table :data="users" style="width: 100%">
              <el-table-column prop="id" label="ID" width="80" />
              <el-table-column prop="phone" label="手机号" width="150" />
              <el-table-column prop="nickname" label="昵称" width="120" />
              <el-table-column prop="role" label="角色" width="100">
                <template #default="scope">
                  <el-tag :type="getRoleType(scope.row.role)">{{ getRoleName(scope.row.role) }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="status" label="状态" width="100">
                <template #default="scope">
                  <el-tag :type="scope.row.status === 1 ? 'success' : 'danger'">
                    {{ scope.row.status === 1 ? '正常' : '禁用' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="createTime" label="创建时间" width="180" />
              <el-table-column label="操作" width="150">
                <template #default="scope">
                  <el-button type="primary" size="small" @click="editUser(scope.row)">
                    编辑
                  </el-button>
                  <el-button size="small" @click="deleteUser(scope.row.id)" :type="scope.row.status === 1 ? 'danger' : 'success'">
                    {{ scope.row.status === 1 ? '禁用' : '启用' }}
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>

          <!-- 学校管理 -->
          <div v-if="activeMenu === 'schools'" class="content-card card">
            <div class="section-title">
              <el-icon><OfficeBuilding /></el-icon>
              <span>学校管理</span>
            </div>
            <div class="admin-actions">
              <el-button type="primary" @click="dialogVisible = true">
                <el-icon><Plus /></el-icon>添加学校
              </el-button>
            </div>
            <el-table :data="schools" style="width: 100%">
              <el-table-column prop="id" label="ID" width="80" />
              <el-table-column prop="name" label="学校名称" />
              <el-table-column prop="city" label="城市" width="120" />
              <el-table-column prop="level" label="级别" width="100" />
              <el-table-column prop="type" label="类型" width="100" />
              <el-table-column label="操作" width="150">
                <template #default="scope">
                  <el-button type="primary" size="small" @click="editSchool(scope.row)">
                    编辑
                  </el-button>
                  <el-button size="small" type="danger" @click="deleteSchool(scope.row.id)">
                    删除
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>

          <!-- 政策管理 -->
          <div v-if="activeMenu === 'policies'" class="content-card card">
            <div class="section-title">
              <el-icon><Document /></el-icon>
              <span>政策管理</span>
            </div>
            <div class="admin-actions">
              <el-button type="primary" @click="dialogVisible = true">
                <el-icon><Plus /></el-icon>添加政策
              </el-button>
            </div>
            <el-table :data="policies" style="width: 100%">
              <el-table-column prop="id" label="ID" width="80" />
              <el-table-column prop="title" label="政策标题" />
              <el-table-column prop="type" label="类型" width="120" />
              <el-table-column prop="publishDate" label="发布日期" width="150" />
              <el-table-column label="操作" width="150">
                <template #default="scope">
                  <el-button type="primary" size="small" @click="editPolicy(scope.row)">
                    编辑
                  </el-button>
                  <el-button size="small" type="danger" @click="deletePolicy(scope.row.id)">
                    删除
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>

          <!-- 学生管理 -->
          <div v-if="activeMenu === 'students'" class="content-card card">
            <div class="section-title">
              <el-icon><Reading /></el-icon>
              <span>学生管理</span>
            </div>
            <div class="admin-actions">
              <el-button type="primary" @click="dialogVisible = true">
                <el-icon><Plus /></el-icon>添加学生
              </el-button>
            </div>
            <el-table :data="students" style="width: 100%">
              <el-table-column prop="id" label="ID" width="80" />
              <el-table-column prop="name" label="姓名" width="120" />
              <el-table-column prop="phone" label="手机号" width="150" />
              <el-table-column prop="school" label="所在学校" />
              <el-table-column prop="grade" label="年级" width="100" />
              <el-table-column label="操作" width="150">
                <template #default="scope">
                  <el-button type="primary" size="small" @click="editStudent(scope.row)">
                    编辑
                  </el-button>
                  <el-button size="small" type="danger" @click="deleteStudent(scope.row.id)">
                    删除
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-col>
      </el-row>
    </div>

    <!-- 编辑对话框 -->
    <el-dialog v-model="dialogVisible" title="编辑信息" width="600px">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="120px">
        <!-- 动态表单内容 -->
        <template v-if="activeMenu === 'users'">
          <el-form-item label="手机号" prop="phone">
            <el-input v-model="form.phone" placeholder="请输入手机号" />
          </el-form-item>
          <el-form-item label="昵称" prop="nickname">
            <el-input v-model="form.nickname" placeholder="请输入昵称" />
          </el-form-item>
          <el-form-item label="密码" prop="password">
            <el-input v-model="form.password" type="password" placeholder="请输入密码" />
          </el-form-item>
          <el-form-item label="角色" prop="role">
            <el-select v-model="form.role" placeholder="请选择角色">
              <el-option label="考生/家长" value="1" />
              <el-option label="学校" value="2" />
              <el-option label="管理员" value="3" />
            </el-select>
          </el-form-item>
          <el-form-item label="状态" prop="status">
            <el-select v-model="form.status" placeholder="请选择状态">
              <el-option label="正常" value="1" />
              <el-option label="禁用" value="0" />
            </el-select>
          </el-form-item>
        </template>

        <template v-if="activeMenu === 'schools'">
          <el-form-item label="学校名称" prop="name">
            <el-input v-model="form.name" placeholder="请输入学校名称" />
          </el-form-item>
          <el-form-item label="城市" prop="city">
            <el-input v-model="form.city" placeholder="请输入城市" />
          </el-form-item>
          <el-form-item label="级别" prop="level">
            <el-input v-model="form.level" placeholder="请输入级别" />
          </el-form-item>
          <el-form-item label="类型" prop="type">
            <el-input v-model="form.type" placeholder="请输入类型" />
          </el-form-item>
          <el-form-item label="地址" prop="address">
            <el-input v-model="form.address" placeholder="请输入地址" />
          </el-form-item>
        </template>

        <template v-if="activeMenu === 'policies'">
          <el-form-item label="政策标题" prop="title">
            <el-input v-model="form.title" placeholder="请输入政策标题" />
          </el-form-item>
          <el-form-item label="类型" prop="type">
            <el-input v-model="form.type" placeholder="请输入政策类型" />
          </el-form-item>
          <el-form-item label="发布日期" prop="publishDate">
            <el-date-picker v-model="form.publishDate" type="date" placeholder="请选择发布日期" />
          </el-form-item>
          <el-form-item label="内容" prop="content">
            <el-input v-model="form.content" type="textarea" :rows="4" placeholder="请输入政策内容" />
          </el-form-item>
        </template>

        <template v-if="activeMenu === 'students'">
          <el-form-item label="姓名" prop="name">
            <el-input v-model="form.name" placeholder="请输入姓名" />
          </el-form-item>
          <el-form-item label="手机号" prop="phone">
            <el-input v-model="form.phone" placeholder="请输入手机号" />
          </el-form-item>
          <el-form-item label="所在学校" prop="school">
            <el-input v-model="form.school" placeholder="请输入所在学校" />
          </el-form-item>
          <el-form-item label="年级" prop="grade">
            <el-input v-model="form.grade" placeholder="请输入年级" />
          </el-form-item>
        </template>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="saveForm">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { 
  User, OfficeBuilding, Document, Reading, Menu, 
  Plus, Edit, Delete, Check, Warning 
} from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/store'
import axios from 'axios'

const router = useRouter()
const userStore = useUserStore()
const activeMenu = ref('users')
const dialogVisible = ref(false)
const formRef = ref(null)

// 表单数据
const form = reactive({})

// 表单验证规则
const rules = reactive({
  phone: [{ required: true, message: '请输入手机号', trigger: 'blur' }],
  nickname: [{ required: true, message: '请输入昵称', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
  role: [{ required: true, message: '请选择角色', trigger: 'change' }],
  status: [{ required: true, message: '请选择状态', trigger: 'change' }],
  name: [{ required: true, message: '请输入名称', trigger: 'blur' }],
  city: [{ required: true, message: '请输入城市', trigger: 'blur' }],
  level: [{ required: true, message: '请输入级别', trigger: 'blur' }],
  type: [{ required: true, message: '请输入类型', trigger: 'blur' }],
  title: [{ required: true, message: '请输入标题', trigger: 'blur' }],
  publishDate: [{ required: true, message: '请选择发布日期', trigger: 'change' }],
  content: [{ required: true, message: '请输入内容', trigger: 'blur' }]
})

// 数据
const users = ref([])
const schools = ref([])
const policies = ref([])
const students = ref([])

// 加载数据
const loadUsers = async () => {
  try {
    const response = await axios.get('/api/admin/users')
    users.value = response.data
  } catch (error) {
    ElMessage.error('获取用户列表失败')
  }
}

const loadSchools = async () => {
  try {
    const response = await axios.get('/api/admin/schools')
    schools.value = response.data
  } catch (error) {
    ElMessage.error('获取学校列表失败')
  }
}

const loadPolicies = async () => {
  try {
    const response = await axios.get('/api/admin/policies')
    policies.value = response.data
  } catch (error) {
    ElMessage.error('获取政策列表失败')
  }
}

const loadStudents = async () => {
  try {
    const response = await axios.get('/api/admin/students')
    students.value = response.data
  } catch (error) {
    ElMessage.error('获取学生列表失败')
  }
}

// 加载数据
const loadData = () => {
  switch (activeMenu.value) {
    case 'users':
      loadUsers()
      break
    case 'schools':
      loadSchools()
      break
    case 'policies':
      loadPolicies()
      break
    case 'students':
      loadStudents()
      break
  }
}

// 监听菜单变化，加载对应数据
watch(activeMenu, () => {
  loadData()
})

// 角色类型
const getRoleType = (role) => {
  switch (role) {
    case 1: return 'info'
    case 2: return 'warning'
    case 3: return 'danger'
    default: return 'info'
  }
}

// 角色名称
const getRoleName = (role) => {
  switch (role) {
    case 1: return '考生/家长'
    case 2: return '学校'
    case 3: return '管理员'
    default: return '未知'
  }
}

// 编辑用户
const editUser = (user) => {
  form.id = user.id
  form.phone = user.phone
  form.nickname = user.nickname
  form.role = user.role
  form.status = user.status
  dialogVisible.value = true
}

// 删除用户
const deleteUser = async (id) => {
  ElMessage.confirm('确定要删除这个用户吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await axios.delete(`/api/admin/users/${id}`)
      ElMessage.success('删除成功！')
      loadUsers()
    } catch (error) {
      ElMessage.error('删除失败：' + error.message)
    }
  })
}

// 编辑学校
const editSchool = (school) => {
  form.id = school.id
  form.name = school.name
  form.city = school.city
  form.level = school.level
  form.type = school.type
  dialogVisible.value = true
}

// 删除学校
const deleteSchool = async (id) => {
  ElMessage.confirm('确定要删除这个学校吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await axios.delete(`/api/admin/schools/${id}`)
      ElMessage.success('删除成功！')
      loadSchools()
    } catch (error) {
      ElMessage.error('删除失败：' + error.message)
    }
  })
}

// 编辑政策
const editPolicy = (policy) => {
  form.id = policy.id
  form.title = policy.title
  form.type = policy.type
  form.publishDate = policy.publishDate
  form.content = policy.content
  dialogVisible.value = true
}

// 删除政策
const deletePolicy = async (id) => {
  ElMessage.confirm('确定要删除这个政策吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await axios.delete(`/api/admin/policies/${id}`)
      ElMessage.success('删除成功！')
      loadPolicies()
    } catch (error) {
      ElMessage.error('删除失败：' + error.message)
    }
  })
}

// 编辑学生
const editStudent = (student) => {
  form.id = student.id
  form.name = student.name
  form.phone = student.phone
  form.school = student.school
  form.grade = student.grade
  dialogVisible.value = true
}

// 删除学生
const deleteStudent = async (id) => {
  ElMessage.confirm('确定要删除这个学生吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await axios.delete(`/api/admin/students/${id}`)
      ElMessage.success('删除成功！')
      loadStudents()
    } catch (error) {
      ElMessage.error('删除失败：' + error.message)
    }
  })
}

// 保存表单
const saveForm = async () => {
  formRef.value.validate(async (valid) => {
    if (valid) {
      try {
        let response
        if (activeMenu.value === 'users') {
          if (form.id) {
            response = await axios.put(`/api/admin/users/${form.id}`, form)
          } else {
            response = await axios.post('/api/admin/users', form)
          }
        } else if (activeMenu.value === 'schools') {
          if (form.id) {
            response = await axios.put(`/api/admin/schools/${form.id}`, form)
          } else {
            response = await axios.post('/api/admin/schools', form)
          }
        } else if (activeMenu.value === 'policies') {
          if (form.id) {
            response = await axios.put(`/api/admin/policies/${form.id}`, form)
          } else {
            response = await axios.post('/api/admin/policies', form)
          }
        } else if (activeMenu.value === 'students') {
          if (form.id) {
            response = await axios.put(`/api/admin/students/${form.id}`, form)
          } else {
            response = await axios.post('/api/admin/students', form)
          }
        }
        ElMessage.success('保存成功！')
        dialogVisible.value = false
        loadData()
      } catch (error) {
        ElMessage.error('保存失败：' + error.message)
      }
    }
  })
}

// 检查权限并加载数据
onMounted(() => {
  if (!userStore.isLoggedIn || userStore.userInfo?.role !== 3) {
    ElMessage.error('权限不足，需要管理员权限')
    router.push('/')
  } else {
    loadData()
  }
})
</script>

<style scoped>
.admin-page {
  min-height: 100%;
  background: var(--bg-secondary);
}

.page-header {
  background: var(--primary-gradient);
  color: var(--text-primary);
  padding: 48px 0;
  margin-bottom: 32px;
}

.container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 32px;
}

.page-title {
  font-size: 36px;
  font-weight: 700;
  margin-bottom: 12px;
  color: var(--text-primary);
}

.page-desc {
  font-size: 16px;
  opacity: 0.9;
  color: var(--text-secondary);
}

.card {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  padding: 28px;
  margin-bottom: 24px;
  backdrop-filter: blur(10px);
}

.section-title {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border-color);
}

.section-title .el-icon {
  font-size: 22px;
  color: #667eea;
}

.admin-menu {
  background: transparent;
  border: none;
}

.admin-menu :deep(.el-menu-item) {
  height: 56px;
  line-height: 56px;
  font-size: 15px;
  margin-bottom: 8px;
  border-radius: 12px;
  transition: color 0.3s, background-color 0.3s, border-color 0.3s, box-shadow 0.3s, transform 0.3s;
  color: rgba(255, 255, 255, 0.7);
  background: transparent;
}

.admin-menu :deep(.el-menu-item:hover) {
  background: rgba(102, 126, 234, 0.1);
  color: #fff;
}

.admin-menu :deep(.el-menu-item.is-active) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
}

.content-card {
  min-height: 500px;
}

.admin-actions {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 20px;
}

:deep(.el-form-item__label) {
  color: rgba(255, 255, 255, 0.7);
}

:deep(.el-input__wrapper) {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: none;
}

:deep(.el-input__wrapper:hover) {
  border-color: rgba(102, 126, 234, 0.3);
}

:deep(.el-input__wrapper.is-focus) {
  border-color: #667eea;
  box-shadow: 0 0 10px rgba(102, 126, 234, 0.2);
}

:deep(.el-input__inner) {
  color: #fff;
}

:deep(.el-input__inner::placeholder) {
  color: rgba(255, 255, 255, 0.3);
}

:deep(.el-select .el-input__wrapper) {
  background: rgba(255, 255, 255, 0.05);
}

:deep(.el-select-dropdown) {
  background: #16213e;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

:deep(.el-select-dropdown__item) {
  color: rgba(255, 255, 255, 0.8);
}

:deep(.el-select-dropdown__item:hover) {
  background: rgba(102, 126, 234, 0.15);
}

:deep(.el-select-dropdown__item.selected) {
  color: #667eea;
}

:deep(.el-button--primary) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
}

:deep(.el-button--primary:hover) {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
}

:deep(.el-button--default) {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.8);
}

:deep(.el-button--default:hover) {
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
}

:deep(.el-table) {
  background: transparent;
  color: rgba(255, 255, 255, 0.8);
}

:deep(.el-table th.el-table__cell) {
  background: rgba(255, 255, 255, 0.05);
  color: rgba(255, 255, 255, 0.7);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

:deep(.el-table td.el-table__cell) {
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

:deep(.el-table--enable-row-hover .el-table__body tr:hover > td.el-table__cell) {
  background: rgba(102, 126, 234, 0.1);
}

:deep(.el-dialog) {
  background: rgba(26, 26, 46, 0.95);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  backdrop-filter: blur(20px);
}

:deep(.el-dialog__header) {
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

:deep(.el-dialog__title) {
  color: #fff;
  font-size: 18px;
  font-weight: 600;
}

:deep(.el-dialog__footer) {
  border-top: 1px solid rgba(255, 255, 255, 0.08);
}

:deep(.el-date-picker__header) {
  background: #16213e;
  color: #fff;
}

:deep(.el-date-picker__body) {
  background: #16213e;
  color: #fff;
}

:deep(.el-date-picker__cell) {
  color: #fff;
}

:deep(.el-date-picker__cell:hover) {
  background: rgba(102, 126, 234, 0.2);
}

:deep(.el-date-picker__cell.is-selected) {
  background: #667eea;
}

@media (max-width: 768px) {
  .page-header {
    padding: 32px 0;
  }

  .page-title {
    font-size: 28px;
  }

  .admin-actions {
    justify-content: center;
  }
}
</style>
