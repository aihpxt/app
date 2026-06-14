<template>
  <div class="feedback-widget">
    <div class="feedback-button" @click="showDialog = true">
      <el-icon :size="24"><Edit /></el-icon>
      <span class="button-text">反馈</span>
    </div>

    <el-dialog v-model="showDialog" title="意见反馈" width="500px">
      <div class="feedback-content">
        <el-form :model="feedbackForm" label-width="100px">
          <el-form-item label="反馈类型">
            <el-radio-group v-model="feedbackForm.type">
              <el-radio value="suggestion">功能建议</el-radio>
              <el-radio value="bug">问题反馈</el-radio>
              <el-radio value="praise">使用表扬</el-radio>
            </el-radio-group>
          </el-form-item>

          <el-form-item label="反馈内容">
            <el-input
              v-model="feedbackForm.content"
              type="textarea"
              :rows="4"
              placeholder="请详细描述您的问题或建议..."
            />
          </el-form-item>

          <el-form-item label="联系方式（选填）">
            <el-input
              v-model="feedbackForm.contact"
              placeholder="手机号或邮箱，方便我们回复您"
            />
          </el-form-item>
        </el-form>
      </div>
      <template #footer>
        <el-button @click="showDialog = false">取消</el-button>
        <el-button type="primary" @click="submitFeedback" :loading="submitting">
          提交反馈
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { Edit } from '@element-plus/icons-vue'
import { aiApi } from '@/api'

export default {
  name: 'FeedbackWidget',
  components: {
    Edit
  },
  setup() {
    const showDialog = ref(false)
    const submitting = ref(false)

    const feedbackForm = reactive({
      type: 'suggestion',
      content: '',
      contact: ''
    })

    const submitFeedback = async () => {
      if (!feedbackForm.content.trim()) {
        ElMessage.warning('请填写反馈内容')
        return
      }

      submitting.value = true

      try {
        const response = await aiApi.submitFeedback({
          type: feedbackForm.type,
          content: feedbackForm.content,
          contact: feedbackForm.contact
        })
        
        ElMessage.success(response.message || '感谢您的反馈！我们会尽快处理。')
        showDialog.value = false
        feedbackForm.type = 'suggestion'
        feedbackForm.content = ''
        feedbackForm.contact = ''
      } catch (error) {
        ElMessage.error('提交反馈失败，请稍后重试')
      } finally {
        submitting.value = false
      }
    }

    return {
      showDialog,
      submitting,
      feedbackForm,
      submitFeedback
    }
  }
}
</script>

<style scoped>
.feedback-widget {
  position: fixed;
  right: 20px;
  bottom: 100px;
  z-index: 1000;
}

.feedback-button {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
  transition: color 0.3s ease, background-color 0.3s ease, border-color 0.3s ease, box-shadow 0.3s ease, transform 0.3s ease;
}

.feedback-button:hover {
  transform: scale(1.1);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.5);
}

.button-text {
  font-size: 12px;
  margin-top: 2px;
}

@media (max-width: 768px) {
  .feedback-widget {
    right: 10px;
    bottom: 80px;
  }

  .feedback-button {
    width: 48px;
    height: 48px;
  }

  .button-text {
    display: none;
  }
}
</style>
