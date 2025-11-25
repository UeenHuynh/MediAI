import React, { useState, useEffect, useRef } from 'react';
import { 
  Activity, 
  Users, 
  AlertTriangle, 
  HeartPulse, 
  Thermometer, 
  Droplet, 
  Wind, 
  Brain, 
  Clock, 
  FileText, 
  Search,
  ChevronRight,
  LayoutDashboard,
  Settings,
  LogOut,
  Menu,
  Shield,
  Lock,
  CheckCircle,
  MessageCircle,
  X,
  HelpCircle,
  ArrowRight,
  Bell,
  BarChart2,
  GitCommit,
  Database,
  Sliders,
  RefreshCw
} from 'lucide-react';

// --- MOCK DATA ---

const MOCK_NOTIFICATIONS = [
  { id: 1, type: 'danger', title: 'Cảnh báo Sepsis Khẩn cấp', msg: 'Bệnh nhân Nguyễn Văn A có nguy cơ Sepsis tăng vọt (89%).', time: '2 phút trước' },
  { id: 2, type: 'warning', title: 'Model Drift Detected', msg: 'Độ chính xác mô hình Mortality giảm nhẹ xuống dưới 85%.', time: '1 giờ trước' },
  { id: 3, type: 'success', title: 'ETL Pipeline Hoàn thành', msg: 'Dữ liệu MIMIC-IV mới nhất đã được nạp thành công.', time: '3 giờ trước' },
  { id: 4, type: 'info', title: 'Hệ thống bảo trì', msg: 'Lịch bảo trì định kỳ vào 2:00 AM ngày mai.', time: '5 giờ trước' },
];

const MOCK_PATIENTS = [
  {
    id: 'P-100234',
    name: 'Nguyễn Văn A',
    age: 68,
    gender: 'M',
    admissionDate: '2023-10-24',
    loc: 'ICU-A',
    diagnosis: 'Pneumonia',
    sepsisScore: 0.89, 
    mortalityScore: 0.45,
    readmissionScore: 0.72,
    vitals: { hr: 115, bp: '90/60', spo2: 92, temp: 38.9, rr: 24 },
    labs: { wbc: 16.5, lactate: 4.2, crp: 150, creatinine: 1.8 },
    history: ['Diabetes T2', 'Hypertension'],
    alerts: ['High Sepsis Risk', 'Tachycardia']
  },
  {
    id: 'P-100567',
    name: 'Trần Thị B',
    age: 54,
    gender: 'F',
    admissionDate: '2023-10-25',
    loc: 'ICU-B',
    diagnosis: 'Post-op Cardiac',
    sepsisScore: 0.12, 
    mortalityScore: 0.05,
    readmissionScore: 0.23,
    vitals: { hr: 82, bp: '120/80', spo2: 98, temp: 37.0, rr: 18 },
    labs: { wbc: 6.5, lactate: 1.1, crp: 12, creatinine: 0.9 },
    history: ['None'],
    alerts: []
  },
  {
    id: 'P-100899',
    name: 'Lê Văn C',
    age: 72,
    gender: 'M',
    admissionDate: '2023-10-22',
    loc: 'Med-Surg',
    diagnosis: 'CHF Exacerbation',
    sepsisScore: 0.35,
    mortalityScore: 0.65, 
    readmissionScore: 0.88, 
    vitals: { hr: 95, bp: '110/70', spo2: 94, temp: 36.8, rr: 22 },
    labs: { wbc: 9.0, lactate: 1.8, crp: 45, creatinine: 2.1 },
    history: ['CHF', 'CKD Stage 3'],
    alerts: ['High Readmission Risk']
  }
];

// --- SHARED COMPONENTS ---

const Card = ({ children, className = "" }) => (
  <div className={`bg-white rounded-xl border border-slate-200 shadow-sm ${className}`}>
    {children}
  </div>
);

const Badge = ({ children, type = 'neutral' }) => {
  const styles = {
    danger: 'bg-red-100 text-red-700 border-red-200',
    warning: 'bg-amber-100 text-amber-700 border-amber-200',
    success: 'bg-emerald-100 text-emerald-700 border-emerald-200',
    neutral: 'bg-slate-100 text-slate-700 border-slate-200',
    info: 'bg-blue-100 text-blue-700 border-blue-200',
  };
  return (
    <span className={`px-2.5 py-0.5 rounded-full text-xs font-medium border ${styles[type] || styles.neutral}`}>
      {children}
    </span>
  );
};

const VitalCard = ({ icon: Icon, label, value, unit, status = 'normal' }) => {
  const colors = {
    normal: 'text-slate-900',
    warning: 'text-amber-600',
    danger: 'text-red-600'
  };
  return (
    <Card className="p-4 flex items-center space-x-4">
      <div className={`p-3 rounded-full ${status === 'danger' ? 'bg-red-50' : 'bg-blue-50'}`}>
        <Icon className={`w-6 h-6 ${status === 'danger' ? 'text-red-500' : 'text-blue-500'}`} />
      </div>
      <div>
        <p className="text-sm text-slate-500 font-medium">{label}</p>
        <p className={`text-2xl font-bold ${colors[status]}`}>
          {value} <span className="text-sm text-slate-400 font-normal">{unit}</span>
        </p>
      </div>
    </Card>
  );
};

const ScoreGauge = ({ score, label, colorClass }) => {
  const percentage = Math.round(score * 100);
  return (
    <div className="flex flex-col items-center justify-center p-4">
      <div className="relative w-24 h-24">
        <svg className="w-full h-full" viewBox="0 0 36 36">
          <path d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="#E2E8F0" strokeWidth="3" />
          <path d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="currentColor" strokeWidth="3" strokeDasharray={`${percentage}, 100`} className={colorClass} />
        </svg>
        <div className="absolute inset-0 flex items-center justify-center flex-col">
          <span className={`text-xl font-bold ${colorClass}`}>{percentage}%</span>
        </div>
      </div>
      <p className="mt-2 text-sm font-medium text-slate-600">{label}</p>
    </div>
  );
};

// --- NEW SCREENS: MODEL PERFORMANCE & SETTINGS ---

const ModelMetricCard = ({ title, value, subtitle, trend }) => (
  <div className="bg-slate-50 p-4 rounded-lg border border-slate-200">
    <p className="text-xs text-slate-500 font-medium uppercase">{title}</p>
    <div className="flex items-end justify-between mt-1">
      <h4 className="text-2xl font-bold text-slate-800">{value}</h4>
      <span className={`text-xs font-bold ${trend === 'up' ? 'text-emerald-600' : 'text-red-600'}`}>
        {trend === 'up' ? '↑' : '↓'} {subtitle}
      </span>
    </div>
  </div>
);

const ConfusionMatrix = () => (
  <div className="grid grid-cols-2 gap-1 w-48 h-48">
    <div className="bg-blue-600 rounded-tl-lg flex items-center justify-center text-white flex-col">
      <span className="text-xl font-bold">TP</span>
      <span className="text-xs opacity-80">True Pos</span>
    </div>
    <div className="bg-blue-200 rounded-tr-lg flex items-center justify-center text-blue-900 flex-col">
      <span className="text-xl font-bold">FP</span>
      <span className="text-xs opacity-80">False Pos</span>
    </div>
    <div className="bg-blue-200 rounded-bl-lg flex items-center justify-center text-blue-900 flex-col">
      <span className="text-xl font-bold">FN</span>
      <span className="text-xs opacity-80">False Neg</span>
    </div>
    <div className="bg-blue-600 rounded-br-lg flex items-center justify-center text-white flex-col">
      <span className="text-xl font-bold">TN</span>
      <span className="text-xs opacity-80">True Neg</span>
    </div>
  </div>
);

const ModelPerformanceView = () => {
  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-slate-800">Model Performance Monitoring</h2>
        <div className="flex space-x-2">
            <Badge type="success">Status: Healthy</Badge>
            <span className="text-sm text-slate-500">Last retrained: 2 days ago</span>
        </div>
      </div>

      {/* Model Selector Tabs (Visual only) */}
      <div className="flex border-b border-slate-200">
        <button className="px-4 py-2 border-b-2 border-blue-600 text-blue-600 font-bold text-sm">Sepsis (XGBoost)</button>
        <button className="px-4 py-2 border-b-2 border-transparent text-slate-500 hover:text-slate-700 font-medium text-sm">Readmission (LightGBM)</button>
        <button className="px-4 py-2 border-b-2 border-transparent text-slate-500 hover:text-slate-700 font-medium text-sm">Mortality (RandomForest)</button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Metrics */}
        <Card className="p-6 lg:col-span-2 space-y-6">
            <h3 className="font-bold text-slate-800 flex items-center">
                <Activity className="w-5 h-5 mr-2 text-blue-600" /> Key Performance Indicators (Test Set)
            </h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <ModelMetricCard title="AUROC" value="0.89" subtitle="1.2%" trend="up" />
                <ModelMetricCard title="F1-Score" value="0.84" subtitle="0.5%" trend="up" />
                <ModelMetricCard title="Precision" value="0.78" subtitle="2.1%" trend="down" />
                <ModelMetricCard title="Recall" value="0.91" subtitle="1.5%" trend="up" />
            </div>
            
            <div className="mt-6">
                <h4 className="text-sm font-semibold text-slate-700 mb-4">Feature Importance (SHAP Summary)</h4>
                <div className="space-y-3">
                    {[
                        { name: 'Lactate Level', val: 90 },
                        { name: 'WBC Count', val: 75 },
                        { name: 'Systolic BP', val: 60 },
                        { name: 'Age', val: 40 },
                        { name: 'Respiratory Rate', val: 35 }
                    ].map((f) => (
                        <div key={f.name} className="flex items-center">
                            <span className="w-32 text-xs text-slate-600 font-medium">{f.name}</span>
                            <div className="flex-1 h-2 bg-slate-100 rounded-full mx-2">
                                <div className="h-2 bg-blue-500 rounded-full" style={{ width: `${f.val}%` }}></div>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </Card>

        {/* Confusion Matrix & Drift */}
        <div className="space-y-6">
            <Card className="p-6 flex flex-col items-center">
                <h3 className="font-bold text-slate-800 mb-4 w-full">Confusion Matrix</h3>
                <ConfusionMatrix />
                <div className="mt-4 text-xs text-slate-500 text-center">
                    <p>High Recall optimized to reduce False Negatives (Missed Sepsis cases).</p>
                </div>
            </Card>

            <Card className="p-6">
                <h3 className="font-bold text-slate-800 mb-2 flex items-center">
                    <Wind className="w-5 h-5 mr-2 text-amber-500" /> Data Drift Check
                </h3>
                <p className="text-sm text-slate-600 mb-3">Comparing distribution of current ICU vitals vs. training data.</p>
                <div className="space-y-2">
                    <div className="flex justify-between text-xs">
                        <span>Covariate Shift</span>
                        <span className="text-emerald-600 font-bold">Low</span>
                    </div>
                    <div className="flex justify-between text-xs">
                        <span>Concept Drift</span>
                        <span className="text-emerald-600 font-bold">None detected</span>
                    </div>
                </div>
                <button className="mt-4 w-full py-2 bg-slate-100 text-slate-700 text-xs font-bold rounded hover:bg-slate-200 flex items-center justify-center">
                    <RefreshCw className="w-3 h-3 mr-2" /> Retrain Model
                </button>
            </Card>
        </div>
      </div>
    </div>
  );
};

const SettingsView = () => (
    <div className="max-w-3xl mx-auto animate-fade-in">
        <h2 className="text-2xl font-bold text-slate-800 mb-6">System Settings</h2>
        
        <Card className="mb-6">
            <div className="p-4 border-b border-slate-200 bg-slate-50 flex items-center">
                <Sliders className="w-5 h-5 mr-2 text-slate-600" />
                <h3 className="font-bold text-slate-700">Model Thresholds</h3>
            </div>
            <div className="p-6 space-y-6">
                <div>
                    <div className="flex justify-between mb-1">
                        <label className="text-sm font-medium text-slate-700">Sepsis Alert Threshold</label>
                        <span className="text-sm font-bold text-blue-600">0.70</span>
                    </div>
                    <input type="range" min="0" max="1" step="0.05" defaultValue="0.7" className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer" />
                    <p className="text-xs text-slate-500 mt-1">Alerts will trigger if model probability exceeds 70%.</p>
                </div>
                <div>
                    <div className="flex justify-between mb-1">
                        <label className="text-sm font-medium text-slate-700">Readmission Risk Threshold</label>
                        <span className="text-sm font-bold text-blue-600">0.50</span>
                    </div>
                    <input type="range" min="0" max="1" step="0.05" defaultValue="0.5" className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer" />
                </div>
            </div>
        </Card>

        <Card>
            <div className="p-4 border-b border-slate-200 bg-slate-50 flex items-center">
                <Bell className="w-5 h-5 mr-2 text-slate-600" />
                <h3 className="font-bold text-slate-700">Notification Preferences</h3>
            </div>
            <div className="p-6 space-y-4">
                <div className="flex items-center justify-between">
                    <div>
                        <p className="text-sm font-medium text-slate-800">High Priority Alerts (Red)</p>
                        <p className="text-xs text-slate-500">Immediate popup for sepsis/mortality risks.</p>
                    </div>
                    <div className="relative inline-block w-12 h-6 transition duration-200 ease-in-out">
                         <div className="w-10 h-6 bg-blue-600 rounded-full shadow-inner"></div>
                         <div className="absolute w-4 h-4 bg-white rounded-full shadow left-1 top-1 translate-x-4 transition-transform"></div>
                    </div>
                </div>
                <div className="border-t border-slate-100 pt-4 flex items-center justify-between">
                    <div>
                        <p className="text-sm font-medium text-slate-800">Daily Report Digest</p>
                        <p className="text-xs text-slate-500">Email summary of ICU statistics at 8:00 AM.</p>
                    </div>
                     <div className="relative inline-block w-12 h-6 transition duration-200 ease-in-out">
                         <div className="w-10 h-6 bg-slate-300 rounded-full shadow-inner"></div>
                         <div className="absolute w-4 h-4 bg-white rounded-full shadow left-1 top-1 transition-transform"></div>
                    </div>
                </div>
            </div>
        </Card>
    </div>
);

// --- EXISTING COMPONENTS ---
const ChatBotWidget = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([
    { type: 'bot', text: 'Xin chào! Tôi là trợ lý ảo MediAI. Bạn cần hỗ trợ gì về cách đăng nhập hoặc quy định bảo mật?' }
  ]);
  const [input, setInput] = useState('');

  const handleSend = () => {
    if (!input.trim()) return;
    setMessages([...messages, { type: 'user', text: input }]);
    setInput('');
    setTimeout(() => {
      setMessages(prev => [...prev, { type: 'bot', text: 'Cảm ơn câu hỏi của bạn. Hệ thống đang trong giai đoạn Demo Portfolio. Vui lòng liên hệ admin Minh Uyên để được cấp quyền truy cập.' }]);
    }, 1000);
  };

  return (
    <div className="fixed bottom-6 right-6 z-50">
      {!isOpen && (
        <button 
          onClick={() => setIsOpen(true)}
          className="bg-blue-600 hover:bg-blue-700 text-white p-4 rounded-full shadow-lg transition-all transform hover:scale-110 flex items-center justify-center"
        >
          <HelpCircle className="w-8 h-8" />
        </button>
      )}

      {isOpen && (
        <div className="bg-white w-80 h-96 rounded-2xl shadow-2xl flex flex-col border border-slate-200 animate-fade-in-up">
          <div className="bg-blue-600 text-white p-4 rounded-t-2xl flex justify-between items-center">
            <div className="flex items-center">
              <MessageCircle className="w-5 h-5 mr-2" />
              <span className="font-semibold">MediAI Support</span>
            </div>
            <button onClick={() => setIsOpen(false)} className="text-blue-100 hover:text-white">
              <X className="w-5 h-5" />
            </button>
          </div>
          <div className="flex-1 p-4 overflow-y-auto bg-slate-50 space-y-3">
            {messages.map((m, i) => (
              <div key={i} className={`flex ${m.type === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-[80%] p-3 rounded-lg text-sm ${m.type === 'user' ? 'bg-blue-600 text-white' : 'bg-white text-slate-800 shadow-sm border border-slate-200'}`}>
                  {m.text}
                </div>
              </div>
            ))}
          </div>
          <div className="p-3 border-t border-slate-200 bg-white rounded-b-2xl flex">
            <input 
              type="text" 
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Nhập câu hỏi..."
              className="flex-1 border border-slate-300 rounded-l-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-500"
              onKeyPress={(e) => e.key === 'Enter' && handleSend()}
            />
            <button 
              onClick={handleSend}
              className="bg-blue-600 text-white px-4 py-2 rounded-r-lg text-sm hover:bg-blue-700"
            >
              Gửi
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

const ComplianceModal = ({ onAccept, onDecline }) => {
  return (
    <div className="fixed inset-0 bg-slate-900/80 backdrop-blur-sm z-40 flex items-center justify-center p-4">
      <div className="bg-white max-w-2xl w-full rounded-2xl shadow-2xl overflow-hidden animate-scale-in">
        <div className="bg-amber-50 p-6 border-b border-amber-100 flex items-center">
          <AlertTriangle className="w-8 h-8 text-amber-600 mr-4" />
          <div>
            <h2 className="text-xl font-bold text-amber-900">Quy định Bảo mật & Tuân thủ Dữ liệu</h2>
            <p className="text-sm text-amber-700">Vui lòng đọc kỹ trước khi truy cập hệ thống.</p>
          </div>
        </div>
        
        <div className="p-6 max-h-[60vh] overflow-y-auto space-y-4 text-slate-700">
          <p className="font-medium">Hệ thống MediAI xử lý Dữ liệu Sức khỏe được Bảo vệ (PHI). Việc truy cập trái phép là vi phạm pháp luật nghiêm trọng.</p>
          
          <div className="space-y-2 pl-4 border-l-4 border-blue-100">
            <h4 className="font-bold text-slate-900">1. Tuân thủ HIPAA & GDPR</h4>
            <p className="text-sm">Người dùng cam kết tuân thủ các quy định về quyền riêng tư của bệnh nhân theo tiêu chuẩn HIPAA (Mỹ) và GDPR (Châu Âu).</p>
          </div>

          <div className="space-y-2 pl-4 border-l-4 border-blue-100">
            <h4 className="font-bold text-slate-900">2. Mục đích sử dụng</h4>
            <p className="text-sm">Hệ thống này chỉ phục vụ mục đích Demo Portfolio kỹ thuật. Dữ liệu hiển thị là dữ liệu giả lập từ bộ dữ liệu MIMIC-IV đã được ẩn danh (de-identified).</p>
          </div>

          <div className="space-y-2 pl-4 border-l-4 border-blue-100">
            <h4 className="font-bold text-slate-900">3. Ghi nhật ký truy cập (Audit Logs)</h4>
            <p className="text-sm">Mọi hành động của bạn trên hệ thống (xem, tìm kiếm, xuất dữ liệu) đều được ghi lại để phục vụ mục đích kiểm toán an ninh.</p>
          </div>

          <p className="text-xs text-slate-500 mt-4 italic">
            Bằng cách nhấn "Tôi Đồng Ý", bạn xác nhận rằng bạn đã hiểu và chấp nhận các điều khoản trên. Bạn chịu hoàn toàn trách nhiệm về việc bảo mật tài khoản được cấp.
          </p>
        </div>

        <div className="p-6 bg-slate-50 border-t border-slate-200 flex justify-end space-x-4">
          <button 
            onClick={onDecline}
            className="px-6 py-2.5 text-slate-600 font-medium hover:bg-slate-200 rounded-lg transition-colors"
          >
            Từ chối
          </button>
          <button 
            onClick={onAccept}
            className="px-6 py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-bold rounded-lg shadow-md flex items-center transition-all transform hover:scale-105"
          >
            <CheckCircle className="w-5 h-5 mr-2" />
            Tôi Đồng Ý
          </button>
        </div>
      </div>
    </div>
  );
};

const LandingPage = ({ onStart }) => (
  <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 flex flex-col items-center justify-center p-4 relative overflow-hidden text-white">
    <div className="absolute top-0 left-0 w-full h-full overflow-hidden z-0 opacity-20">
      <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-blue-500 rounded-full blur-[128px]"></div>
      <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-purple-500 rounded-full blur-[128px]"></div>
    </div>

    <div className="z-10 text-center max-w-3xl animate-fade-in">
      <div className="mb-8 flex justify-center">
        <div className="w-24 h-24 bg-blue-600 rounded-2xl flex items-center justify-center shadow-2xl transform rotate-12">
          <Activity className="w-12 h-12 text-white" />
        </div>
      </div>
      
      <h1 className="text-5xl md:text-7xl font-extrabold mb-6 tracking-tight">
        Medi<span className="text-blue-400">AI</span> Platform
      </h1>
      <p className="text-xl md:text-2xl text-blue-100 mb-12 font-light">
        Nền tảng Phân tích Dữ liệu Y tế & Dự đoán Lâm sàng Thông minh
      </p>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-16 text-left">
        <div className="bg-white/10 backdrop-blur-lg p-6 rounded-xl border border-white/10 hover:bg-white/20 transition-colors">
          <Brain className="w-8 h-8 text-blue-300 mb-4" />
          <h3 className="font-bold text-lg mb-2">AI Predictions</h3>
          <p className="text-sm text-blue-200">Sepsis, Readmission & Mortality modeling with XGBoost.</p>
        </div>
        <div className="bg-white/10 backdrop-blur-lg p-6 rounded-xl border border-white/10 hover:bg-white/20 transition-colors">
          <Activity className="w-8 h-8 text-emerald-300 mb-4" />
          <h3 className="font-bold text-lg mb-2">Real-time Vitals</h3>
          <p className="text-sm text-blue-200">Live streaming data simulation from MIMIC-IV pipeline.</p>
        </div>
        <div className="bg-white/10 backdrop-blur-lg p-6 rounded-xl border border-white/10 hover:bg-white/20 transition-colors">
          <Shield className="w-8 h-8 text-amber-300 mb-4" />
          <h3 className="font-bold text-lg mb-2">Secure & Compliant</h3>
          <p className="text-sm text-blue-200">Designed with HIPAA/GDPR compliance best practices.</p>
        </div>
      </div>

      <button 
        onClick={onStart}
        className="group relative inline-flex items-center justify-center px-8 py-4 font-bold text-white transition-all duration-200 bg-blue-600 font-pj rounded-full focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-600 hover:bg-blue-500 hover:shadow-xl hover:-translate-y-1"
      >
        Truy Cập Hệ Thống
        <ArrowRight className="w-5 h-5 ml-2 group-hover:translate-x-1 transition-transform" />
      </button>
      
      <p className="mt-8 text-xs text-slate-400">
        © 2024 Minh Uyên Portfolio. MIMIC-IV Data Integration.
      </p>
    </div>
  </div>
);

const AuthPage = ({ onLogin }) => {
  const [isRegister, setIsRegister] = useState(false);
  
  return (
    <div className="min-h-screen bg-slate-100 flex items-center justify-center p-4">
      <div className="bg-white w-full max-w-md rounded-2xl shadow-xl overflow-hidden flex flex-col animate-fade-in">
        <div className="bg-slate-900 p-8 text-center relative overflow-hidden">
           <div className="absolute top-0 left-0 w-full h-full bg-blue-600 opacity-10"></div>
           <div className="relative z-10">
             <div className="w-16 h-16 bg-blue-600 rounded-xl flex items-center justify-center shadow-lg mx-auto mb-4">
                <Activity className="w-8 h-8 text-white" />
             </div>
             <h2 className="text-2xl font-bold text-white">MediAI Portal</h2>
             <p className="text-blue-200 text-sm mt-1">Secure Clinical Access</p>
           </div>
        </div>

        <div className="p-8">
          <h3 className="text-xl font-bold text-slate-800 mb-6 text-center">
            {isRegister ? 'Đăng Ký Tài Khoản' : 'Đăng Nhập Hệ Thống'}
          </h3>
          
          <div className="space-y-4">
            {isRegister && (
              <div>
                <label className="block text-xs font-bold text-slate-500 uppercase mb-1">Họ và Tên</label>
                <div className="relative">
                  <Users className="w-5 h-5 text-slate-400 absolute left-3 top-2.5" />
                  <input type="text" className="w-full pl-10 pr-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" placeholder="Bs. Nguyễn Văn A" />
                </div>
              </div>
            )}
            
            <div>
              <label className="block text-xs font-bold text-slate-500 uppercase mb-1">Email / ID Nhân sự</label>
              <div className="relative">
                <FileText className="w-5 h-5 text-slate-400 absolute left-3 top-2.5" />
                <input type="email" className="w-full pl-10 pr-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" placeholder="doctor@hospital.org" />
              </div>
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-500 uppercase mb-1">Mật khẩu</label>
              <div className="relative">
                <Lock className="w-5 h-5 text-slate-400 absolute left-3 top-2.5" />
                <input type="password" className="w-full pl-10 pr-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" placeholder="••••••••" />
              </div>
            </div>

            <button 
              onClick={onLogin}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 rounded-lg shadow-md hover:shadow-lg transition-all transform active:scale-95 mt-4"
            >
              {isRegister ? 'Tạo Tài Khoản' : 'Đăng Nhập'}
            </button>
          </div>

          <div className="mt-6 text-center">
            <p className="text-sm text-slate-600">
              {isRegister ? 'Đã có tài khoản?' : 'Chưa có tài khoản?'} 
              <button 
                onClick={() => setIsRegister(!isRegister)}
                className="text-blue-600 font-bold ml-2 hover:underline"
              >
                {isRegister ? 'Đăng nhập ngay' : 'Đăng ký'}
              </button>
            </p>
          </div>
        </div>
        
        <div className="bg-slate-50 p-4 text-center border-t border-slate-200">
          <p className="text-xs text-slate-400 flex items-center justify-center">
            <Lock className="w-3 h-3 mr-1" /> Protected by MediAI Shield 256-bit Encryption
          </p>
        </div>
      </div>
    </div>
  );
};

// --- UPDATED DASHBOARD (With Switch Logic) ---

const Dashboard = ({ onLogout }) => {
  const [activeTab, setActiveTab] = useState('dashboard'); // dashboard, patients, performance, settings
  const [selectedPatient, setSelectedPatient] = useState(null);
  const [currentTime, setCurrentTime] = useState(new Date());
  const [showNotifications, setShowNotifications] = useState(false);

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  const handlePatientClick = (patient) => {
    setSelectedPatient(patient);
    setActiveTab('patient-detail');
  };

  // Render Dashboard (Monitoring) Content
  const renderDashboardContent = () => (
     <div className="space-y-6 animate-fade-in">
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="p-4 border-l-4 border-blue-500">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-sm text-slate-500">Total Patients</p>
              <h3 className="text-2xl font-bold text-slate-800">142</h3>
            </div>
            <Users className="text-blue-500" />
          </div>
        </Card>
        <Card className="p-4 border-l-4 border-red-500">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-sm text-slate-500">High Sepsis Risk</p>
              <h3 className="text-2xl font-bold text-red-600">8</h3>
            </div>
            <AlertTriangle className="text-red-500" />
          </div>
          <p className="text-xs text-red-500 mt-2 font-medium">Requires immediate attention</p>
        </Card>
        <Card className="p-4 border-l-4 border-amber-500">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-sm text-slate-500">High Readmission Risk</p>
              <h3 className="text-2xl font-bold text-amber-600">15</h3>
            </div>
            <Clock className="text-amber-500" />
          </div>
        </Card>
        <Card className="p-4 border-l-4 border-emerald-500">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-sm text-slate-500">Discharge Ready</p>
              <h3 className="text-2xl font-bold text-emerald-600">24</h3>
            </div>
            <FileText className="text-emerald-500" />
          </div>
        </Card>
      </div>

      <Card className="overflow-hidden">
        <div className="p-4 border-b border-slate-200 flex justify-between items-center bg-slate-50">
          <h3 className="font-semibold text-slate-800 flex items-center">
            <Activity className="w-4 h-4 mr-2 text-blue-600" /> 
            Live ICU Monitor
          </h3>
          <div className="relative">
            <Search className="w-4 h-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400" />
            <input 
              type="text" 
              placeholder="Search ID or Name..." 
              className="pl-9 pr-4 py-1.5 text-sm border border-slate-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left">
            <thead className="text-xs text-slate-500 uppercase bg-slate-50 border-b">
              <tr>
                <th className="px-6 py-3">Patient</th>
                <th className="px-6 py-3">Location</th>
                <th className="px-6 py-3">Diagnosis</th>
                <th className="px-6 py-3">Sepsis Risk</th>
                <th className="px-6 py-3">Status</th>
                <th className="px-6 py-3">Action</th>
              </tr>
            </thead>
            <tbody>
              {MOCK_PATIENTS.map((p) => (
                <tr key={p.id} className="bg-white border-b hover:bg-slate-50 transition-colors">
                  <td className="px-6 py-4 font-medium text-slate-900">
                    {p.name} <br/>
                    <span className="text-xs text-slate-500">{p.id}</span>
                  </td>
                  <td className="px-6 py-4">{p.loc}</td>
                  <td className="px-6 py-4">{p.diagnosis}</td>
                  <td className="px-6 py-4">
                    {p.sepsisScore > 0.7 ? (
                      <Badge type="danger">High ({Math.round(p.sepsisScore * 100)}%)</Badge>
                    ) : p.sepsisScore > 0.3 ? (
                      <Badge type="warning">Medium ({Math.round(p.sepsisScore * 100)}%)</Badge>
                    ) : (
                      <Badge type="success">Low ({Math.round(p.sepsisScore * 100)}%)</Badge>
                    )}
                  </td>
                  <td className="px-6 py-4">
                    {p.alerts.length > 0 ? (
                      <div className="flex items-center text-red-600 text-xs font-bold">
                        <AlertTriangle className="w-3 h-3 mr-1" /> {p.alerts[0]}
                      </div>
                    ) : (
                      <span className="text-emerald-600 text-xs font-bold">Stable</span>
                    )}
                  </td>
                  <td className="px-6 py-4">
                    <button 
                      onClick={() => handlePatientClick(p)}
                      className="text-blue-600 hover:text-blue-800 font-medium text-xs flex items-center"
                    >
                      View Details <ChevronRight className="w-3 h-3 ml-1" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );

  const renderPatientDetail = () => {
    if (!selectedPatient) return <div>Select a patient</div>;
    const p = selectedPatient;
    return (
      <div className="space-y-6 animate-fade-in">
        <div className="flex items-center space-x-2 text-sm text-slate-500 mb-4">
          <span onClick={() => setActiveTab('dashboard')} className="cursor-pointer hover:text-blue-600 hover:underline">Dashboard</span>
          <ChevronRight className="w-4 h-4" />
          <span>Patient Details</span>
          <ChevronRight className="w-4 h-4" />
          <span className="font-semibold text-slate-800">{p.name}</span>
        </div>
        {/* ... (Patient Header Info) ... */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
          <div className="flex items-center space-x-4">
            <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center text-blue-600 font-bold text-2xl">
              {p.name.charAt(0)}
            </div>
            <div>
              <h2 className="text-2xl font-bold text-slate-800">{p.name}</h2>
              <div className="flex space-x-4 text-sm text-slate-500 mt-1">
                <span>ID: {p.id}</span>
                <span>|</span>
                <span>{p.age} yrs</span>
                <span>|</span>
                <span>{p.gender}</span>
                <span>|</span>
                <span className="flex items-center"><AlertTriangle className="w-3 h-3 mr-1" /> {p.diagnosis}</span>
              </div>
            </div>
          </div>
          <div className="mt-4 md:mt-0 flex space-x-3">
            <button className="px-4 py-2 bg-white border border-slate-300 text-slate-700 rounded-lg text-sm font-medium hover:bg-slate-50">
              View History
            </button>
            <button className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 shadow-sm">
              Add Clinical Note
            </button>
          </div>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          <VitalCard icon={HeartPulse} label="Heart Rate" value={p.vitals.hr} unit="bpm" status={p.vitals.hr > 100 ? 'danger' : 'normal'} />
          <VitalCard icon={Activity} label="BP" value={p.vitals.bp} unit="mmHg" status={p.vitals.bp.startsWith('90') ? 'warning' : 'normal'} />
          <VitalCard icon={Wind} label="SpO2" value={`${p.vitals.spo2}%`} unit="" status={p.vitals.spo2 < 95 ? 'warning' : 'normal'} />
          <VitalCard icon={Thermometer} label="Temp" value={p.vitals.temp} unit="°C" status={p.vitals.temp > 38 ? 'danger' : 'normal'} />
          <VitalCard icon={Droplet} label="Resp Rate" value={p.vitals.rr} unit="bpm" status={p.vitals.rr > 20 ? 'warning' : 'normal'} />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-6">
            <Card className="p-6 border-l-4 border-red-500">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-bold text-slate-800 flex items-center">
                  <Brain className="w-5 h-5 mr-2 text-purple-600" />
                  Sepsis Early Warning (XGBoost)
                </h3>
                <Badge type={p.sepsisScore > 0.7 ? 'danger' : 'success'}>Model Accuracy: 89%</Badge>
              </div>
              <div className="flex items-center space-x-8">
                <ScoreGauge score={p.sepsisScore} label="Sepsis Risk" colorClass={p.sepsisScore > 0.7 ? 'text-red-600' : 'text-emerald-500'} />
                <div className="flex-1">
                  <h4 className="text-sm font-semibold text-slate-700 mb-2">Top Contributing Factors (SHAP):</h4>
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-slate-600">Lactate Level ({p.labs.lactate} mmol/L)</span>
                      <span className="text-red-600 font-bold">+35% risk</span>
                    </div>
                    <div className="w-full bg-slate-100 rounded-full h-2">
                      <div className="bg-red-500 h-2 rounded-full" style={{width: '85%'}}></div>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-slate-600">WBC Count ({p.labs.wbc})</span>
                      <span className="text-amber-600 font-bold">+15% risk</span>
                    </div>
                    <div className="w-full bg-slate-100 rounded-full h-2">
                      <div className="bg-amber-500 h-2 rounded-full" style={{width: '45%'}}></div>
                    </div>
                  </div>
                </div>
              </div>
            </Card>
             {/* ... Lab Results Table ... */}
             <Card>
              <div className="p-4 border-b border-slate-200 bg-slate-50">
                 <h3 className="font-semibold text-slate-800">Recent Lab Results (MIMIC-IV)</h3>
              </div>
              <table className="w-full text-sm text-left">
                <thead className="text-xs text-slate-500 uppercase bg-white border-b">
                  <tr>
                    <th className="px-6 py-3">Test</th>
                    <th className="px-6 py-3">Value</th>
                    <th className="px-6 py-3">Ref Range</th>
                    <th className="px-6 py-3">Trend</th>
                  </tr>
                </thead>
                <tbody>
                  <tr className="border-b">
                    <td className="px-6 py-3 font-medium">Lactate</td>
                    <td className={`px-6 py-3 font-bold ${p.labs.lactate > 2 ? 'text-red-600' : ''}`}>{p.labs.lactate}</td>
                    <td className="px-6 py-3 text-slate-500">0.5 - 2.0</td>
                    <td className="px-6 py-3 text-red-500">↑ Rising</td>
                  </tr>
                  <tr className="border-b">
                    <td className="px-6 py-3 font-medium">WBC</td>
                    <td className={`px-6 py-3 font-bold ${p.labs.wbc > 11 ? 'text-red-600' : ''}`}>{p.labs.wbc}</td>
                    <td className="px-6 py-3 text-slate-500">4.5 - 11.0</td>
                    <td className="px-6 py-3 text-red-500">↑ Rising</td>
                  </tr>
                  <tr className="border-b">
                    <td className="px-6 py-3 font-medium">Creatinine</td>
                    <td className="px-6 py-3">{p.labs.creatinine}</td>
                    <td className="px-6 py-3 text-slate-500">0.6 - 1.2</td>
                    <td className="px-6 py-3 text-amber-500">→ Stable High</td>
                  </tr>
                </tbody>
              </table>
            </Card>
          </div>

          <div className="space-y-6">
             {/* ... Readmission & Mortality Cards ... */}
             <Card className="p-6">
               <h3 className="text-sm font-bold text-slate-500 uppercase tracking-wider mb-4">Readmission Prediction</h3>
               <div className="mb-4">
                 <div className="flex justify-between items-end mb-1">
                   <span className="text-3xl font-bold text-slate-800">{Math.round(p.readmissionScore * 100)}%</span>
                   <span className="text-sm text-slate-500">30-day risk</span>
                 </div>
                 <div className="w-full bg-slate-100 rounded-full h-3">
                    <div className={`h-3 rounded-full ${p.readmissionScore > 0.5 ? 'bg-amber-500' : 'bg-emerald-500'}`} style={{width: `${p.readmissionScore * 100}%`}}></div>
                 </div>
               </div>
               <ul className="space-y-2 text-sm">
                 <li className="flex items-center text-slate-600"><AlertTriangle className="w-4 h-4 mr-2 text-amber-500" /> History: {p.history.join(', ')}</li>
                 <li className="flex items-center text-slate-600"><Activity className="w-4 h-4 mr-2 text-blue-500" /> LOS: 5 days (Longer than avg)</li>
               </ul>
            </Card>
             <Card className="p-6">
               <h3 className="text-sm font-bold text-slate-500 uppercase tracking-wider mb-4">Mortality Prediction</h3>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-slate-600">In-Hospital Mortality</span>
                  <span className={`font-bold ${p.mortalityScore > 0.5 ? 'text-red-600' : 'text-slate-800'}`}>{Math.round(p.mortalityScore * 100)}%</span>
                </div>
                <p className="text-xs text-slate-400">Based on Random Forest (AUROC 0.88)</p>
            </Card>
            <Card className="p-6 bg-blue-50 border-blue-100">
               <h3 className="text-sm font-bold text-blue-800 mb-2 flex items-center"><FileText className="w-4 h-4 mr-2" /> NLP Extraction</h3>
               <p className="text-sm text-blue-900 italic">"Patient appears agitated. Family history of cardiac issues noted in intake form..."</p>
               <div className="flex flex-wrap gap-2 mt-3">
                 <Badge type="neutral">#Agitated</Badge>
                 <Badge type="neutral">#CardiacHistory</Badge>
               </div>
            </Card>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="flex h-screen bg-slate-100 font-sans text-slate-900 animate-fade-in">
      {/* SIDEBAR */}
      <aside className="w-64 bg-slate-900 text-slate-300 flex flex-col shadow-xl">
        <div className="p-6 flex items-center space-x-3 border-b border-slate-800">
          <div className="bg-blue-600 p-2 rounded-lg">
            <Activity className="text-white w-6 h-6" />
          </div>
          <div>
            <h1 className="text-white font-bold text-lg leading-tight">MediAI</h1>
            <p className="text-xs text-slate-500">MIMIC-IV Platform</p>
          </div>
        </div>

        <nav className="flex-1 py-6 px-3 space-y-1">
          <button 
            onClick={() => setActiveTab('dashboard')}
            className={`w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg transition-colors ${activeTab === 'dashboard' ? 'bg-blue-600 text-white' : 'hover:bg-slate-800'}`}
          >
            <LayoutDashboard className="w-5 h-5" />
            <span>Dashboard</span>
          </button>
          <button 
            onClick={() => setActiveTab('patients')}
            className={`w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg transition-colors ${(activeTab === 'patients' || activeTab === 'patient-detail') ? 'bg-blue-600 text-white' : 'hover:bg-slate-800'}`}
          >
            <Users className="w-5 h-5" />
            <span>Patients</span>
          </button>
          <button 
            onClick={() => setActiveTab('performance')}
            className={`w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg transition-colors ${activeTab === 'performance' ? 'bg-blue-600 text-white' : 'hover:bg-slate-800'}`}
          >
            <BarChart2 className="w-5 h-5" />
            <span>Model Performance</span>
          </button>
          <button 
             onClick={() => setActiveTab('settings')}
             className={`w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg transition-colors ${activeTab === 'settings' ? 'bg-blue-600 text-white' : 'hover:bg-slate-800'}`}
          >
            <Settings className="w-5 h-5" />
            <span>Settings</span>
          </button>
        </nav>

        <div className="p-4 border-t border-slate-800">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-blue-500 to-purple-500 flex items-center justify-center text-white font-bold text-xs">
              MU
            </div>
            <div>
              <p className="text-sm text-white font-medium">Minh Uyên</p>
              <p className="text-xs text-slate-500">Data Engineer</p>
            </div>
          </div>
        </div>
      </aside>

      {/* MAIN CONTENT */}
      <main className="flex-1 overflow-y-auto flex flex-col">
        {/* Topbar */}
        <header className="bg-white h-16 border-b border-slate-200 flex justify-between items-center px-6 sticky top-0 z-10 shadow-sm">
          <div className="flex items-center text-slate-500 text-sm">
            <Clock className="w-4 h-4 mr-2" />
            {currentTime.toLocaleString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' })}
          </div>
          <div className="flex items-center space-x-4">
            {/* NOTIFICATION DROPDOWN */}
            <div className="relative">
              <button 
                onClick={() => setShowNotifications(!showNotifications)}
                className="p-2 text-slate-400 hover:text-slate-600 relative focus:outline-none"
              >
                <Bell className="w-5 h-5" />
                <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full border-2 border-white"></span>
              </button>

              {showNotifications && (
                <div className="absolute right-0 mt-2 w-80 bg-white rounded-xl shadow-2xl border border-slate-200 z-50 animate-fade-in-up">
                  <div className="p-3 border-b border-slate-100 flex justify-between items-center">
                    <h3 className="text-sm font-bold text-slate-800">Notifications</h3>
                    <button onClick={() => setShowNotifications(false)} className="text-slate-400 hover:text-slate-600"><X className="w-4 h-4"/></button>
                  </div>
                  <div className="max-h-80 overflow-y-auto">
                    {MOCK_NOTIFICATIONS.map((n) => (
                      <div key={n.id} className="p-3 hover:bg-slate-50 border-b border-slate-50 last:border-0 cursor-pointer">
                        <div className="flex items-start">
                           <div className={`w-2 h-2 mt-1.5 rounded-full mr-2 ${n.type === 'danger' ? 'bg-red-500' : n.type === 'warning' ? 'bg-amber-500' : 'bg-blue-500'}`}></div>
                           <div>
                             <p className="text-sm font-medium text-slate-800">{n.title}</p>
                             <p className="text-xs text-slate-500 mt-0.5">{n.msg}</p>
                             <p className="text-[10px] text-slate-400 mt-1">{n.time}</p>
                           </div>
                        </div>
                      </div>
                    ))}
                  </div>
                  <div className="p-2 text-center border-t border-slate-100">
                    <button className="text-xs text-blue-600 font-medium hover:underline">View All Alerts</button>
                  </div>
                </div>
              )}
            </div>

            <button 
              onClick={onLogout}
              className="p-2 text-slate-400 hover:text-red-600"
            >
              <LogOut className="w-5 h-5" />
            </button>
          </div>
        </header>

        <div className="p-6 max-w-7xl mx-auto w-full">
          {activeTab === 'dashboard' && renderDashboardContent()}
          {activeTab === 'patients' && renderDashboardContent()}
          {activeTab === 'patient-detail' && renderPatientDetail()}
          {activeTab === 'performance' && <ModelPerformanceView />}
          {activeTab === 'settings' && <SettingsView />}
        </div>
      </main>
    </div>
  );
};

// --- ROOT APP ---

export default function App() {
  const [currentView, setCurrentView] = useState('landing'); 
  
  const goToCompliance = () => setCurrentView('compliance');
  const goToAuth = () => setCurrentView('auth');
  const goToDashboard = () => setCurrentView('dashboard');
  const handleLogout = () => setCurrentView('auth');

  return (
    <>
      {currentView === 'landing' && <LandingPage onStart={goToCompliance} />}
      
      {currentView === 'compliance' && (
        <>
          <LandingPage onStart={() => {}} /> 
          <ComplianceModal onAccept={goToAuth} onDecline={() => setCurrentView('landing')} />
        </>
      )}
      
      {currentView === 'auth' && <AuthPage onLogin={goToDashboard} />}
      
      {currentView === 'dashboard' && <Dashboard onLogout={handleLogout} />}

      {currentView !== 'dashboard' && <ChatBotWidget />}
    </>
  );
}