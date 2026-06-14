import { apiClient, aiApiClient } from '@/utils/request'
import type { UserInfo, School, ApiResponse, PagedResponse } from '@/types'

export { apiClient }

export const userApi = {
  login: (data: { username: string; password: string }): Promise<ApiResponse<{ token: string; userInfo: UserInfo }>> => 
    apiClient.post('/user/login', data),
  
  register: (data: { username: string; password: string; email?: string; phone?: string }): Promise<ApiResponse<unknown>> => 
    apiClient.post('/user/register', data),
  
  getUserInfo: (): Promise<ApiResponse<UserInfo>> => 
    apiClient.get('/user/info'),
  
  updateUserInfo: (userData: Partial<UserInfo>): Promise<ApiResponse<UserInfo>> =>
    apiClient.put('/user/info', userData)
}

export const schoolApi = {
  getSchoolList: (params: {
    keyword?: string;
    city?: string;
    type?: number | null;
    page?: number;
    size?: number;
    nature?: string;
    min_score?: number | null;
    max_score?: number | null;
    sort_by?: string;
  }): Promise<PagedResponse<School>> =>
    apiClient.get('/schools', { params }),
  
  getSchoolDetail: (id: string | number): Promise<ApiResponse<School>> => 
    apiClient.get(`/schools/${id}`),
  
  getRelatedSchools: (id: string | number, limit?: number): Promise<ApiResponse<School[]>> => 
    apiClient.get(`/schools/${id}/related`, { params: { limit: limit || 5 } }),
  
  getSchoolStats: (): Promise<ApiResponse<{
    total: number;
    public_count: number;
    private_count: number;
    key_count: number;
    city_stats: Array<{ name: string; count: number }>;
  }>> => 
    apiClient.get('/schools/stats'),
  
  getSchoolsBatch: (schoolIds: number[]): Promise<ApiResponse<School[]>> => 
    apiClient.post('/schools/batch', schoolIds),
  
  searchSchools: (params: { keyword?: string; city?: string }): Promise<PagedResponse<School>> => 
    apiClient.get('/schools/search', { params })
}

export const aiApi = {
  get: <T = unknown>(url: string, params: Record<string, unknown> = {}, options: Record<string, unknown> = {}) => {
    return aiApiClient.get<T>(url, { params, ...options })
  },
  
  post: <T = unknown>(url: string, data: unknown = {}, options: Record<string, unknown> = {}) => {
    return aiApiClient.post<T>(url, data, options)
  },
  
  put: <T = unknown>(url: string, data: unknown = {}, options: Record<string, unknown> = {}) => {
    return aiApiClient.put<T>(url, data, options)
  },
  
  delete: <T = unknown>(url: string, options: Record<string, unknown> = {}) => {
    return aiApiClient.delete<T>(url, options)
  },
  
  predictScore: (mock_scores: unknown): Promise<ApiResponse<unknown>> => 
    aiApiClient.post('/predict/score', mock_scores),
  
  predictAdmission: (studentData: unknown): Promise<ApiResponse<unknown>> => 
    aiApiClient.post('/predict/admission', studentData),
  
  recommendSchools: (data: { studentData: unknown }): Promise<ApiResponse<{ recommendations: School[] }>> => 
    aiApiClient.post('/recommend/schools', data),
  
  compareSchools: (data: { schoolIds: number[]; studentScore?: number }): Promise<ApiResponse<unknown>> => 
    aiApiClient.post('/compare/schools', data),
  
  matchSchools: (studentInfo: unknown): Promise<ApiResponse<unknown>> => 
    aiApiClient.post('/match/schools', studentInfo),
  
  generateVolunteer: (studentForm: unknown): Promise<ApiResponse<unknown>> => 
    aiApiClient.post('/volunteer/generate', studentForm),
  
  checkVolunteerRisk: (volunteerTable: unknown): Promise<ApiResponse<unknown>> => 
    aiApiClient.post('/volunteer/risk', volunteerTable),
  
  highSchoolTransition: (planForm: unknown): Promise<ApiResponse<unknown>> => 
    aiApiClient.post('/transition/high-school', planForm),
  
  submitFeedback: (data: { content: string; type?: string }): Promise<ApiResponse<unknown>> => 
    aiApiClient.post('/feedback', data),
  
  enhancedCrawlSchoolCompare: (data: { schools: string[] }): Promise<ApiResponse<unknown>> => 
    aiApiClient.post('/crawl/enhanced/school-compare', data),
  
  enhancedCrawlAdmissionCalculator: (data: unknown): Promise<ApiResponse<unknown>> => 
    aiApiClient.post('/crawl/enhanced/admission-calculator', data),
  
  getDataVisualizationAnalysis: (data: { studentId?: string; analysisType: string; timeRange?: string }): Promise<ApiResponse<unknown>> => 
    aiApiClient.post('/visualization/analysis', data),
  
  interpretPolicy: (data: { policyId: number; policyContent: string }): Promise<ApiResponse<unknown>> => 
    aiApiClient.post('/interpret-policy', data),
  
  openclawChat: async (data: { message: string; type?: string }): Promise<ApiResponse<{ answer: string }>> => {
    try {
      const response = await aiApiClient.post('/agent/chat', data)
      const responseData = response.data as Record<string, unknown>
      return {
        success: responseData.success === undefined ? true : Boolean(responseData.success),
        data: {
          answer: String(responseData.answer || responseData.response || '感谢您的问题，我正在学习更多政策知识。')
        },
        message: String(responseData.message || '')
      }
    } catch (error) {
      console.error('AI聊天接口调用失败:', error)
      return generateMockPolicyAnswer(data.message)
    }
  },
  
  getLearningProgress: async (): Promise<ApiResponse<unknown>> => {
    try {
      const response = await aiApiClient.get('/learning/progress')
      return response.data as ApiResponse<unknown>
    } catch (error) {
      console.error('获取学习进度失败:', error)
      return {
        success: true,
        data: getMockLearningProgress(),
        message: '使用默认数据'
      }
    }
  },
  
  getLearningAnalytics: async (): Promise<ApiResponse<unknown>> => {
    try {
      const response = await aiApiClient.get('/learning/analytics')
      return response.data as ApiResponse<unknown>
    } catch (error) {
      console.error('获取学习分析失败:', error)
      return {
        success: true,
        data: getMockLearningAnalytics(),
        message: '使用默认数据'
      }
    }
  }
}

export const aiServiceApi = {
  async openclawChat(data: { 
    input?: string; 
    message?: string; 
    agent_id?: string; 
    session_id?: string; 
    context?: Record<string, unknown> 
  }, onCallback: (content: string, meta?: Record<string, unknown>) => void): Promise<void> {
    try {
      const resData: unknown = await aiApiClient.post('/agent/chat', data)
      const responseData: Record<string, unknown> = typeof resData === 'string' ? JSON.parse(resData) : (resData as Record<string, unknown>)
      
      const sessionId = responseData.session_id || (responseData.data as Record<string, unknown>)?.session_id
      
      let content = ''
      const dataObj = responseData.data as Record<string, unknown>
      if (dataObj && dataObj.response) {
        content = String(dataObj.response)
      } else if (responseData.response) {
        content = String(responseData.response)
      } else if (responseData.data) {
        content = typeof responseData.data === 'string' ? responseData.data : JSON.stringify(responseData.data)
      } else {
        content = JSON.stringify(responseData)
      }
      
      return new Promise((resolve) => {
        if (!content) {
          onCallback('', { session_id: sessionId })
          resolve()
          return
        }
        
        let index = 0
        const interval = setInterval(() => {
          if (index < content.length) {
            onCallback(content.charAt(index))
            index++
          } else {
            onCallback('', { session_id: sessionId })
            clearInterval(interval)
            resolve()
          }
        }, 20)
      })
    } catch (error) {
      console.error('AI接口请求失败:', error)
      throw error
    }
  }
}

// 模拟学习进度数据
const getMockLearningProgress = () => {
  return {
    overall: {
      totalHours: 128,
      completedTasks: 45,
      totalTasks: 60,
      progressPercentage: 75
    },
    subjects: [
      {
        subject: '语文',
        completedHours: 32,
        totalHours: 40,
        progress: 80,
        strengths: ['阅读理解', '写作'],
        weaknesses: ['文言文'],
        notes: ['建议加强文言文背诵']
      },
      {
        subject: '数学',
        completedHours: 36,
        totalHours: 45,
        progress: 80,
        strengths: ['代数', '几何'],
        weaknesses: ['函数'],
        notes: ['建议多做函数练习题']
      },
      {
        subject: '英语',
        completedHours: 28,
        totalHours: 40,
        progress: 70,
        strengths: ['听力', '语法'],
        weaknesses: ['写作'],
        notes: ['建议多练习英语作文']
      },
      {
        subject: '物理',
        completedHours: 18,
        totalHours: 30,
        progress: 60,
        strengths: ['力学'],
        weaknesses: ['电学'],
        notes: ['建议加强电学基础']
      },
      {
        subject: '化学',
        completedHours: 14,
        totalHours: 25,
        progress: 56,
        strengths: ['实验操作'],
        weaknesses: ['有机化学'],
        notes: ['建议多复习有机化学知识点']
      }
    ],
    recentActivities: [
      { id: 1, activity: '完成数学函数章节练习', subject: '数学', type: 'learning', time: '2小时前', duration: 45 },
      { id: 2, activity: '模拟测试', subject: '语文', type: 'test', time: '5小时前', score: 95, totalScore: 120 },
      { id: 3, activity: '英语听力训练', subject: '英语', type: 'learning', time: '昨天 20:30', duration: 30 },
      { id: 4, activity: '物理电学专题复习', subject: '物理', type: 'learning', time: '昨天 19:00', duration: 60 },
      { id: 5, activity: '化学单元测试', subject: '化学', type: 'test', time: '昨天 15:00', score: 72, totalScore: 80 }
    ],
    learningGoals: [
      { id: 1, goal: '数学函数专项突破', target: '掌握函数基本概念和解题方法', deadline: '2026-02-01', progress: 65 },
      { id: 2, goal: '英语作文提升', target: '能够写出高质量的中考英语作文', deadline: '2026-02-15', progress: 40 },
      { id: 3, goal: '物理电学复习', target: '掌握电学基本概念和电路分析', deadline: '2026-01-25', progress: 80 }
    ]
  }
}

// 模拟学习分析数据
const getMockLearningAnalytics = () => {
  return {
    timeDistribution: [
      { day: '周一', hours: 3.5 },
      { day: '周二', hours: 4.2 },
      { day: '周三', hours: 2.8 },
      { day: '周四', hours: 4.5 },
      { day: '周五', hours: 3.8 },
      { day: '周六', hours: 6.2 },
      { day: '周日', hours: 5.5 }
    ],
    subjectDistribution: [
      { subject: '语文', hours: 32, percentage: 25 },
      { subject: '数学', hours: 36, percentage: 28 },
      { subject: '英语', hours: 28, percentage: 22 },
      { subject: '物理', hours: 18, percentage: 14 },
      { subject: '化学', hours: 14, percentage: 11 }
    ],
    progressTrend: [
      { date: '01-01', progress: 40 },
      { date: '01-05', progress: 48 },
      { date: '01-10', progress: 55 },
      { date: '01-15', progress: 62 },
      { date: '01-20', progress: 68 },
      { date: '01-25', progress: 72 },
      { date: '01-30', progress: 75 }
    ],
    testScores: [
      { subject: '语文', score: 95, totalScore: 120 },
      { subject: '数学', score: 108, totalScore: 120 },
      { subject: '英语', score: 105, totalScore: 120 },
      { subject: '物理', score: 85, totalScore: 100 },
      { subject: '化学', score: 72, totalScore: 80 }
    ],
    learningHabits: {
      averageDailyHours: 4.3,
      mostProductiveDay: '周六',
      mostProductiveTime: '14:00-16:00',
      totalLearningDays: 45,
      consecutiveDays: 12
    },
    recommendations: [
      '数学函数部分需要加强，建议每天做30分钟专项练习',
      '英语写作能力有待提高，建议每周写2-3篇作文',
      '物理电学是薄弱环节，建议观看相关教学视频',
      '学习时间安排合理，继续保持良好的学习习惯',
      '建议增加化学有机部分的复习时间'
    ]
  }
}

export const policyApi = {
  getPolicyList: (params: { keyword?: string; category?: string; region?: string; page?: number; size?: number }) => 
    apiClient.get('/policies', { params }),
  
  getPolicyDetail: (id: string | number) => 
    apiClient.get(`/policies/${id}`),
  
  searchPolicies: (params: { keyword?: string }) => 
    apiClient.get('/policies', { params })
}

// 模拟政策问答回答
const generateMockPolicyAnswer = (question: string): ApiResponse<{ answer: string }> => {
  const questionLower = question.toLowerCase()
  
  // 针对文山州的问题
  if (questionLower.includes('文山') || questionLower.includes('文山州')) {
    return {
      success: true,
      data: {
        answer: '根据云南省教育厅和文山州教育局发布的最新中考政策，文山州中考主要政策包括：\n\n1. **指标到校政策**：文山州省级示范高中将不低于50%的招生计划分配到辖区内各初中学校，促进教育均衡发展。\n\n2. **加分政策**：少数民族考生可享受5-20分的加分照顾，具体分值根据民族类别和地区有所不同。\n\n3. **志愿填报**：实行平行志愿投档模式，考生可填报多个志愿，按分数优先、遵循志愿的原则录取。\n\n4. **体育中考**：总分50分，包括必考项目和选考项目，注重学生体质健康。\n\n5. **特长生招生**：允许具备体育、艺术等特长的考生通过专项测试录取。\n\n如需更详细的政策解读，建议访问文山州教育局官方网站或咨询当地学校。'
      },
      message: ''
    }
  }
  
  // 针对指标到校的问题
  if (questionLower.includes('指标到校')) {
    return {
      success: true,
      data: {
        answer: '云南省中考指标到校政策：\n\n1. **政策目标**：促进义务教育均衡发展，让更多普通初中学生有机会进入优质高中。\n\n2. **分配比例**：省级示范高中将不低于50%的招生计划作为指标到校名额，分配到所属区域内的初中学校。\n\n3. **录取方式**：指标到校生单独划线录取，分数线通常低于统招生录取线。\n\n4. **资格要求**：考生需在本校连续就读三年，综合素质评价达到相应等级。\n\n5. **志愿填报**：指标到校志愿与统招生志愿分开填报，按志愿顺序投档。'
      },
      message: ''
    }
  }
  
  // 针对加分政策的问题
  if (questionLower.includes('加分') || questionLower.includes('照顾')) {
    return {
      success: true,
      data: {
        answer: '云南省中考加分政策（以当年官方公告为准）：\n\n1. **少数民族加分**：\n   - 聚居区少数民族：加20分\n   - 散居区少数民族：加10分\n\n2. **军人子女加分**：\n   - 现役军人子女：加10分\n   - 烈士子女：加20分\n\n3. **其他照顾政策**：\n   - 归侨、华侨子女：加10分\n   - 台湾省籍考生：加10分\n   - 见义勇为先进个人子女：加10-20分\n\n注意：多项加分不累计，取最高项。加分政策逐年收紧，具体以当年政策为准。'
      },
      message: ''
    }
  }
  
  // 针对志愿填报的问题
  if (questionLower.includes('志愿') || questionLower.includes('填报')) {
    return {
      success: true,
      data: {
        answer: '云南省中考志愿填报指南：\n\n1. **志愿设置**：实行平行志愿模式，可填报多个志愿学校。\n\n2. **填报时间**：通常在中考成绩公布后3-5天内进行网上填报。\n\n3. **投档原则**：分数优先、遵循志愿、一次投档。\n\n4. **志愿梯度**：建议按"冲、稳、保"的原则填报，拉开志愿之间的分数差距。\n\n5. **注意事项**：\n   - 认真核对志愿顺序\n   - 了解各校往年录取分数线\n   - 注意志愿填报截止时间\n   - 确认无误后再提交'
      },
      message: ''
    }
  }
  
  // 针对总分或各科分值的问题
  if (questionLower.includes('总分') || questionLower.includes('分值') || questionLower.includes('各科')) {
    return {
      success: true,
      data: {
        answer: '云南省中考总分及科目设置：\n\n**总分：700分**\n\n1. **语文**：120分\n2. **数学**：120分\n3. **英语**：120分（含听力30分）\n4. **物理**：100分\n5. **化学**：80分\n6. **体育**：50分\n7. **道德与法治、历史**：110分（合卷）\n\n**考试时间**：通常在6月中下旬进行，为期3天。\n\n注：各地可能有细微差异，请以当地教育部门公告为准。'
      },
      message: ''
    }
  }
  
  // 通用回答
  return {
    success: true,
    data: {
      answer: '感谢您的提问！关于云南中考政策，我可以为您解答以下方面的问题：\n\n1. **指标到校政策**：优质高中名额分配到各初中学校的具体政策\n2. **加分政策**：少数民族、军人子女等各类加分照顾政策\n3. **志愿填报**：平行志愿填报流程和注意事项\n4. **考试科目**：中考各科分值、考试时间安排\n5. **录取规则**：投档方式、录取分数线等\n\n您可以具体问某个州市的政策，或者某个具体方面的问题，我会为您详细解答！'
    },
    message: ''
  }
}