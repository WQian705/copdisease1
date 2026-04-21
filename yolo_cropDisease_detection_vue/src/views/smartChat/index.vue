<template>
	<div class="chat-page layout-padding">
		<div class="chat-shell layout-padding-auto layout-padding-view">
			<section class="chat-hero">
				<div>
					<span class="hero-badge">智能问答</span>
					<h2>面向农业场景的轻量咨询助手</h2>
					<p>保留原有对话请求流程和建议问题入口，只优化视觉节奏、消息气泡和输入区体验。</p>
				</div>
				<div class="hero-side">
					<span>当前模型</span>
					<strong>GPT-3.5 Turbo</strong>
				</div>
			</section>

			<section class="chat-card">
				<div class="chat-header">
					<div>
						<h3>农业智能助手</h3>
						<p>可以提问病害识别、防治建议、栽培管理和用药注意事项。</p>
					</div>
				</div>

				<div class="chat-messages" ref="messageContainer">
					<div v-for="(message, index) in messages" :key="index" :class="['message', message.role === 'user' ? 'user-message' : 'assistant-message']">
						<div class="message-content">
							<div class="avatar">{{ message.role === 'user' ? '我' : 'AI' }}</div>
							<div class="text">{{ message.content }}</div>
						</div>
					</div>
					<div v-if="loading" class="message assistant-message">
						<div class="message-content">
							<div class="avatar">AI</div>
							<div class="text">
								<span class="loading-dots">思考中</span>
							</div>
						</div>
					</div>
				</div>

				<div class="suggested-questions" v-if="messages.length === 1">
					<div class="suggested-title">猜你想问</div>
					<div class="suggested-list">
						<div v-for="(question, index) in suggestedQuestions" :key="index" class="suggested-item" @click="selectQuestion(question)">
							{{ question }}
						</div>
					</div>
				</div>

				<div class="chat-input">
					<el-input
						v-model="userInput"
						type="textarea"
						:rows="3"
						placeholder="请输入您想咨询的问题，按 Ctrl + Enter 也可以发送"
						@keyup.enter.ctrl="sendMessage"
					/>
					<el-button type="primary" :loading="loading" @click="sendMessage" :disabled="!userInput.trim()" class="send-button">
						发送
					</el-button>
				</div>
			</section>
		</div>
	</div>
</template>

<script>
import axios from 'axios'

export default {
	name: 'SmartChat',
	data() {
		return {
			messages: [
				{
					role: 'assistant',
					content: '你好，我是农业智能小助手。你可以向我咨询病害识别、防治建议、作物管理和常见农业问题。',
				},
			],
			userInput: '',
			loading: false,
			suggestedQuestions: [
				'如何防治水稻病害？',
				'玉米常见病虫害有哪些？',
				'小麦生长周期是多少天？',
				'如何提高农作物产量？',
				'农药使用注意事项有哪些？',
				'农作物施肥的最佳时间是什么？',
				'如何识别植物病害症状？',
			],
			apiKey: 'sk-3rG1hl3sdDbbRoqEHr7utZpcbqbufy1miSD9XhLvVxJGAb4W',
		}
	},
	methods: {
		selectQuestion(question) {
			this.userInput = question
			this.sendMessage()
		},
		async sendMessage() {
			if (!this.userInput.trim() || this.loading) return

			const userMessage = this.userInput.trim()
			this.messages.push({
				role: 'user',
				content: userMessage,
			})

			this.userInput = ''
			this.loading = true

			try {
				const response = await axios.post(
					'https://api.chatanywhere.tech/v1/chat/completions',
					{
						model: 'gpt-3.5-turbo',
						messages: [
							...this.messages.map((msg) => ({
								role: msg.role,
								content: msg.content,
							})),
						],
						temperature: 0.7,
					},
					{
						headers: {
							Authorization: `Bearer ${this.apiKey}`,
							'Content-Type': 'application/json',
						},
					}
				)

				this.messages.push({
					role: 'assistant',
					content: response.data.choices[0].message.content,
				})
			} catch (error) {
				this.$message.error('发送消息失败，请稍后重试')
				console.error('Error:', error)
			} finally {
				this.loading = false
				this.$nextTick(() => {
					this.scrollToBottom()
				})
			}
		},
		scrollToBottom() {
			const container = this.$refs.messageContainer
			container.scrollTop = container.scrollHeight
		},
	},
}
</script>

<style scoped>
.chat-page {
	height: 100%;
}

.chat-shell {
	padding: 18px;
	background: rgba(255, 255, 255, 0.88);
}

.chat-hero {
	display: flex;
	justify-content: space-between;
	gap: 16px;
	padding: 24px;
	border-radius: 24px;
	background: linear-gradient(135deg, #143444 0%, #1e625d 54%, #32789a 100%);
	color: #fff;
}

.hero-badge {
	display: inline-flex;
	padding: 7px 12px;
	border-radius: 999px;
	background: rgba(255, 255, 255, 0.12);
	font-size: 12px;
	letter-spacing: 0.12em;
}

.chat-hero h2 {
	margin: 14px 0 8px;
	font-size: 28px;
}

.chat-hero p {
	margin: 0;
	color: rgba(255, 255, 255, 0.82);
	line-height: 1.8;
}

.hero-side {
	min-width: 160px;
	padding: 18px;
	border-radius: 20px;
	background: rgba(255, 255, 255, 0.12);
}

.hero-side span {
	color: rgba(255, 255, 255, 0.72);
	font-size: 13px;
}

.hero-side strong {
	display: block;
	margin-top: 10px;
	font-size: 26px;
}

.chat-card {
	margin-top: 16px;
	padding: 18px;
	border-radius: 22px;
	background: linear-gradient(180deg, #ffffff 0%, #f7faf8 100%);
	box-shadow: 0 18px 34px rgba(31, 52, 84, 0.06);
	min-height: calc(100vh - 250px);
	display: flex;
	flex-direction: column;
}

.chat-header h3 {
	margin: 0 0 6px;
	color: #24384d;
}

.chat-header p {
	margin: 0;
	color: #7d8a98;
}

.chat-messages {
	flex: 1;
	overflow-y: auto;
	padding: 22px 4px 10px;
	scroll-behavior: smooth;
}

.message {
	margin-bottom: 24px;
	display: flex;
	width: 100%;
	animation: messageAppear 0.28s ease forwards;
}

@keyframes messageAppear {
	from {
		opacity: 0;
		transform: translateY(10px);
	}
	to {
		opacity: 1;
		transform: translateY(0);
	}
}

.message-content {
	display: flex;
	align-items: flex-start;
	max-width: 78%;
	gap: 12px;
	word-break: break-word;
}

.user-message .message-content {
	flex-direction: row-reverse;
	margin-left: auto;
}

.assistant-message .message-content {
	margin-right: auto;
}

.avatar {
	width: 40px;
	height: 40px;
	min-width: 40px;
	border-radius: 16px;
	display: flex;
	align-items: center;
	justify-content: center;
	font-size: 13px;
	font-weight: 700;
	background: linear-gradient(135deg, #eaf4ef 0%, #dcebe4 100%);
	color: #345768;
	box-shadow: 0 8px 18px rgba(31, 52, 84, 0.08);
}

.text {
	padding: 14px 16px;
	border-radius: 18px;
	line-height: 1.7;
	font-size: 14px;
	white-space: pre-wrap;
	background: #f5f8f6;
	color: #32465a;
	box-shadow: 0 10px 24px rgba(31, 52, 84, 0.06);
}

.user-message .text {
	background: linear-gradient(135deg, #1f6f58 0%, #2c79a5 100%);
	color: #fff;
	border-top-right-radius: 6px;
}

.assistant-message .text {
	border-top-left-radius: 6px;
}

.suggested-questions {
	padding: 4px 0 16px;
}

.suggested-title {
	margin-bottom: 12px;
	font-size: 16px;
	font-weight: 600;
	color: #294255;
}

.suggested-list {
	display: flex;
	flex-wrap: wrap;
	gap: 10px;
}

.suggested-item {
	padding: 10px 16px;
	background: rgba(31, 111, 88, 0.08);
	border-radius: 999px;
	font-size: 14px;
	color: #1f6f58;
	cursor: pointer;
	transition: all 0.25s ease;
}

.suggested-item:hover {
	transform: translateY(-1px);
	background: rgba(31, 111, 88, 0.14);
}

.chat-input {
	display: flex;
	gap: 12px;
	padding-top: 14px;
	border-top: 1px solid rgba(101, 124, 142, 0.12);
}

.send-button {
	min-width: 110px;
	border: none;
	border-radius: 16px;
	background: linear-gradient(135deg, #1f6f58 0%, #2f8b70 55%, #2c79a5 100%);
	box-shadow: 0 18px 32px rgba(39, 103, 91, 0.2);
}

.chat-input :deep(.el-textarea__inner) {
	min-height: 108px !important;
	border-radius: 18px;
	background: #f5f8f6;
	box-shadow: inset 0 0 0 1px rgba(106, 128, 115, 0.12) !important;
	padding: 14px 16px;
	resize: none;
}

.loading-dots::after {
	content: '...';
	animation: loading 1.4s infinite;
}

@keyframes loading {
	0% {
		content: '.';
	}
	33% {
		content: '..';
	}
	66% {
		content: '...';
	}
}

.chat-messages::-webkit-scrollbar {
	width: 6px;
}

.chat-messages::-webkit-scrollbar-thumb {
	background: rgba(74, 101, 120, 0.24);
	border-radius: 999px;
}

@media (max-width: 992px) {
	.chat-hero {
		flex-direction: column;
	}

	.chat-input {
		flex-direction: column;
	}

	.send-button {
		width: 100%;
		height: 46px;
	}

	.message-content {
		max-width: 100%;
	}
}
</style>
