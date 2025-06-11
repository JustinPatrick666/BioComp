<template>
  <div class="about">
    <h1>关于本系统</h1>
    <section class="about-section">
      <h2>制作团队</h2>
      <ul>
        <li>喻珊琳（团队指导）</li>
        <li>贺前艺（主算法操作）</li>
        <li>卢昶冰（前后端开发）</li>
        <li>刘家辉（数据集测试）</li>
        <li>刘宠（医学顾问）</li>
      </ul>
    </section>
    <section class="about-section">
      <h2>版本信息</h2>
      <p>版本号：v1.0.0</p>
      <p>发布日期：2025年5月24日</p>
    </section>
    <section class="about-section">
      <h2>使用技术</h2>
      <ul>
        <li>前端：Vue 3, Vite, Cornerstone.js, TypeScript</li>
        <li>后端：FastAPI, Python 3</li>
        <li>医学影像处理：cornerstone-wado-image-loader, dicom-parser</li>
        <li>数据库：SQLite</li>
      </ul>
    </section>
  </div>
</template>

<style scoped>
.about {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  padding: 40px 60px;
  color: #222;
  background: #f7fafc;
}
.about-section {
  margin-bottom: 32px;
}
.about-section h2 {
  margin-bottom: 8px;
  color: #0bc5e6;
}
.about-section ul {
  margin: 0;
  padding-left: 20px;
}
</style>
