import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'

// 导入增强样式
import './assets/styles/enhanced.css'

// 按需导入Element Plus组件和样式
import {
  ElButton,
  ElInput,
  ElSelect,
  ElOption,
  ElDialog,
  ElForm,
  ElFormItem,
  ElMessage,
  ElNotification,
  ElLoading,
  ElMenu,
  ElMenuItem,
  ElSubMenu,
  ElDrawer,
  ElCard,
  ElDivider,
  ElEmpty,
  ElTooltip,
  ElBadge,
  ElPopover,
  ElDropdown,
  ElDropdownMenu,
  ElDropdownItem,
  ElAvatar,
  ElIcon,
  ElPagination,
  ElSkeleton,
  ElTimeline,
  ElTimelineItem,
  ElAlert,
  ElRow,
  ElCol,
  ElProgress,
  ElTag,
  ElTable,
  ElTableColumn,
  ElInputNumber,
  ElRadioGroup,
  ElRadio
} from 'element-plus'
import 'element-plus/dist/index.css'

// 导入所有需要的图标
import {
  Menu,
  ChatDotRound,
  TrendCharts,
  Aim,
  Document,
  School,
  Reading,
  DataAnalysis,
  QuestionFilled,
  User,
  Star,
  StarFilled,
  InfoFilled,
  Switch,
  ArrowDown,
  Plus,
  Fold,
  Expand,
  Delete,
  Present,
  Grid,
  Close,
  Loading,
  Timer,
  ArrowRight,
  Check,
  Refresh,
  CircleCheck,
  CirclePlus,
  RefreshRight,
  Clock,
  Bell,
  BellFilled,
  Calendar,
  PieChart,
  Edit,
  Warning,
  MagicStick,
  Download,
  Message,
  Briefcase,
  MapLocation,
  Setting,
  Collection,
  Right,
  OfficeBuilding,
  Phone,
  Filter,
  Search,
  Medal,
  GoldMedal,
  Clock as ClockIcon
} from '@element-plus/icons-vue'

const app = createApp(App)

// 注册需要的Element Plus组件
app.component('ElButton', ElButton)
app.component('ElInput', ElInput)
app.component('ElSelect', ElSelect)
app.component('ElOption', ElOption)
app.component('ElDialog', ElDialog)
app.component('ElForm', ElForm)
app.component('ElFormItem', ElFormItem)
app.component('ElMenu', ElMenu)
app.component('ElMenuItem', ElMenuItem)
app.component('ElSubMenu', ElSubMenu)
app.component('ElDrawer', ElDrawer)
app.component('ElCard', ElCard)
app.component('ElDivider', ElDivider)
app.component('ElEmpty', ElEmpty)
app.component('ElTooltip', ElTooltip)
app.component('ElBadge', ElBadge)
app.component('ElPopover', ElPopover)
app.component('ElDropdown', ElDropdown)
app.component('ElDropdownMenu', ElDropdownMenu)
app.component('ElDropdownItem', ElDropdownItem)
app.component('ElAvatar', ElAvatar)
app.component('ElIcon', ElIcon)
app.component('ElPagination', ElPagination)
app.component('ElSkeleton', ElSkeleton)
app.component('ElTimeline', ElTimeline)
app.component('ElTimelineItem', ElTimelineItem)
app.component('ElAlert', ElAlert)
app.component('ElRow', ElRow)
app.component('ElCol', ElCol)
app.component('ElProgress', ElProgress)
app.component('ElTag', ElTag)
app.component('ElTable', ElTable)
app.component('ElTableColumn', ElTableColumn)
app.component('ElInputNumber', ElInputNumber)
app.component('ElRadioGroup', ElRadioGroup)
app.component('ElRadio', ElRadio)

// 注册需要的图标
app.component('Menu', Menu)
app.component('ChatDotRound', ChatDotRound)
app.component('TrendCharts', TrendCharts)
app.component('Aim', Aim)
app.component('Document', Document)
app.component('School', School)
app.component('Reading', Reading)
app.component('DataAnalysis', DataAnalysis)
app.component('QuestionFilled', QuestionFilled)
app.component('User', User)
app.component('Star', Star)
app.component('StarFilled', StarFilled)
app.component('InfoFilled', InfoFilled)
app.component('SwitchButton', Switch)
app.component('ArrowDown', ArrowDown)
app.component('Plus', Plus)
app.component('Fold', Fold)
app.component('Expand', Expand)
app.component('Delete', Delete)
app.component('Promotion', Present)
app.component('Grid', Grid)
app.component('Close', Close)
app.component('Loading', Loading)
app.component('Timer', Timer)
app.component('ArrowRight', ArrowRight)
app.component('Check', Check)
app.component('Refresh', Refresh)
app.component('CircleCheck', CircleCheck)
app.component('DocumentChecked', CirclePlus)
app.component('RefreshLeft', RefreshRight)
app.component('Clock', Clock)
app.component('Bell', Bell)
app.component('BellFilled', BellFilled)
app.component('Calendar', Calendar)
app.component('PieChart', PieChart)
app.component('Edit', Edit)
app.component('Warning', Warning)
app.component('MagicStick', MagicStick)
app.component('Download', Download)
app.component('Message', Message)
app.component('Trophy', GoldMedal)
app.component('TrophyBase', Medal)
app.component('Calculator', Plus)
app.component('Briefcase', Briefcase)
app.component('Map', MapLocation)
app.component('Setting', Setting)
app.component('Collection', Collection)
app.component('Right', Right)
app.component('OfficeBuilding', OfficeBuilding)
app.component('Phone', Phone)
app.component('View', Document)
app.component('Filter', Filter)
app.component('Search', Search)
app.component('Medal', Medal)

// 注册全局方法
app.config.globalProperties.$message = ElMessage
app.config.globalProperties.$notify = ElNotification
app.config.globalProperties.$loading = ElLoading.service

app.use(store)
app.use(router)

// 全局错误处理
app.config.errorHandler = (err, vm, info) => {
  console.error('Vue错误:', err, info)
  // 可以将错误信息发送到服务器
}

app.mount('#app')
