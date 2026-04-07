import React, { useState, useEffect, useRef } from 'react';
import { 
  Activity, 
  MessageSquare, 
  LayoutDashboard, 
  Settings, 
  LogOut, 
  User, 
  HeartPulse, 
  Stethoscope, 
  Send, 
  Bot, 
  FileText, 
  Thermometer, 
  Droplet,
  Menu,
  X,
  ChevronRight,
  Shield,
  AlertTriangle,
  Search,
  Bell,
  Calendar,
  Mail,
  Phone,
  MapPin,
  Award,
  Clock,
  Briefcase,
  GraduationCap
} from 'lucide-react';

// --- Theme Constants (Bảng màu Deep Medical Ocean) ---
const THEME = {
  colors: {
    bg: "bg-slate-950",
    glass: "bg-white/5 backdrop-blur-xl border-white/10",
    glassHover: "hover:bg-white/10 hover:border-white/20",
    primary: "from-teal-400 to-cyan-500",
    secondary: "from-violet-500 to-fuchsia-500",
    accent: "text-cyan-300",
    textMain: "text-slate-50",
    textMuted: "text-slate-400",
    success: "text-emerald-400 bg-emerald-400/10 border-emerald-400/20",
    warning: "text-amber-400 bg-amber-400/10 border-amber-400/20",
    danger: "text-rose-400 bg-rose-400/10 border-rose-400/20",
  }
};

// --- Types ---
type Page = 'dashboard' | 'chatbot' | 'predict_sepsis' | 'predict_mortality' | 'settings' | 'auth' | 'profile';
type Message = { id: string; text: string; sender: 'user' | 'bot'; timestamp: Date };

// --- Mock Data ---
const MOCK_CHAT_HISTORY: Message[] = [
  { id: '1', text: 'Xin chào BS. Uyên! MediAI đã sẵn sàng hỗ trợ phân tích dữ liệu bệnh nhân.', sender: 'bot', timestamp: new Date() }
];

const SEPSIS_INPUTS = [
  { id: 'prg', label: 'Plasma Glucose', unit: 'mg/dL', min: 0, max: 200, icon: Activity },
  { id: 'pl', label: 'Blood Work (PL)', unit: 'mu U/ml', min: 0, max: 200, icon: Droplet },
  { id: 'pr', label: 'Blood Pressure', unit: 'mm Hg', min: 0, max: 150, icon: HeartPulse },
  { id: 'sk', label: 'Skin Thickness', unit: 'mm', min: 0, max: 100, icon: User },
  { id: 'ts', label: 'Insulin (TS)', unit: 'mu U/ml', min: 0, max: 100, icon: Activity },
  { id: 'm11', label: 'BMI', unit: 'kg/m²', min: 10, max: 50, icon: User },
  { id: 'bd2', label: 'Pedigree Func', unit: 'score', min: 0, max: 20, icon: FileText },
  { id: 'age', label: 'Age', unit: 'years', min: 0, max: 120, icon: Calendar },
];

const MORTALITY_INPUTS = [
  { id: 'heart_rate', label: 'Nhịp tim', unit: 'bpm', min: 30, max: 250, icon: HeartPulse },
  { id: 'sys_bp', label: 'Huyết áp (Sys)', unit: 'mmHg', min: 50, max: 250, icon: Activity },
  { id: 'dias_bp', label: 'Huyết áp (Dia)', unit: 'mmHg', min: 30, max: 150, icon: Activity },
  { id: 'temp', label: 'Nhiệt độ', unit: '°C', min: 30, max: 45, icon: Thermometer },
  { id: 'oxygen', label: 'SpO2', unit: '%', min: 50, max: 100, icon: Droplet },
];

// --- Components ---

// FIX: Added ...props to allow onClick events to pass through to the div
const GlassCard = ({ children, className = '', hoverEffect = false, noPadding = false, ...props }: any) => (
  <div 
    {...props}
    className={`
      relative overflow-hidden
      ${THEME.colors.glass} border shadow-2xl
      rounded-3xl
      ${hoverEffect ? `transition-all duration-500 hover:scale-[1.01] hover:shadow-cyan-500/10 ${THEME.colors.glassHover}` : ''}
      ${noPadding ? '' : 'p-6'}
      ${className}
    `}
  >
    {/* Noise Texture Overlay for authentic Glass feel */}
    <div className="absolute inset-0 opacity-[0.03] pointer-events-none bg-[url('https://grainy-gradients.vercel.app/noise.svg')] bg-repeat mix-blend-overlay"></div>
    {/* Shine effect */}
    <div className="absolute -top-[50%] -left-[50%] w-[200%] h-[200%] bg-gradient-to-br from-white/5 via-transparent to-transparent rotate-45 pointer-events-none" />
    <div className="relative z-10">{children}</div>
  </div>
);

const Button = ({ children, onClick, variant = 'primary', className = '', type = 'button', icon: Icon }: any) => {
  const baseStyle = "px-6 py-3 rounded-2xl font-semibold transition-all duration-300 flex items-center justify-center gap-2 shadow-lg backdrop-blur-md active:scale-95";
  const variants = {
    primary: `bg-gradient-to-r ${THEME.colors.primary} text-white border border-white/20 shadow-cyan-500/30 hover:shadow-cyan-500/50 hover:brightness-110`,
    secondary: "bg-white/5 hover:bg-white/10 text-white border border-white/10",
    danger: "bg-gradient-to-r from-rose-500 to-pink-600 text-white border border-rose-400/30 shadow-rose-500/20",
    ghost: "bg-transparent hover:bg-white/5 text-slate-300 border-transparent"
  };
  
  return (
    <button 
      type={type}
      onClick={onClick} 
      className={`${baseStyle} ${variants[variant as keyof typeof variants]} ${className}`}
    >
      {Icon && <Icon size={18} />}
      {children}
    </button>
  );
};

const InputField = ({ label, type = 'text', placeholder, value, onChange, icon: Icon, unit }: any) => (
  <div className="space-y-2 group">
    {label && <label className="text-xs uppercase tracking-wider text-cyan-200/60 font-semibold ml-1">{label}</label>}
    <div className="relative">
      {Icon && (
        <div className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400 group-focus-within:text-cyan-300 transition-colors duration-300">
          <Icon size={18} />
        </div>
      )}
      <input
        type={type}
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        className={`
          w-full bg-slate-900/40 border border-white/10 
          rounded-2xl py-3.5 ${Icon ? 'pl-12' : 'pl-4'} ${unit ? 'pr-12' : 'pr-4'}
          text-slate-100 placeholder-slate-600 font-medium
          focus:outline-none focus:ring-2 focus:ring-cyan-400/30 focus:border-cyan-400/50 focus:bg-slate-900/60
          transition-all duration-300 backdrop-blur-sm
        `}
      />
      {unit && (
        <div className="absolute right-4 top-1/2 -translate-y-1/2 text-xs font-bold text-slate-500 bg-white/5 px-2 py-1 rounded-md">
          {unit}
        </div>
      )}
    </div>
  </div>
);

const Badge = ({ children, type = 'success' }: { children: React.ReactNode, type?: 'success' | 'warning' | 'danger' | 'neutral' }) => {
  const styles = {
    success: THEME.colors.success,
    warning: THEME.colors.warning,
    danger: THEME.colors.danger,
    neutral: "text-slate-300 bg-white/5 border-white/10"
  };
  return (
    <span className={`px-3 py-1 rounded-full text-xs font-bold border ${styles[type]} backdrop-blur-md`}>
      {children}
    </span>
  );
};

// --- Pages ---

const AuthPage = ({ onLogin }: { onLogin: () => void }) => {
  const [isLogin, setIsLogin] = useState(true);
  
  return (
    <div className={`min-h-screen flex items-center justify-center p-4 relative overflow-hidden ${THEME.colors.bg}`}>
       {/* Cinematic Background */}
       <div className="absolute inset-0">
          <div className="absolute top-0 left-1/4 w-[600px] h-[600px] bg-teal-500/20 rounded-full blur-[120px] animate-pulse" />
          <div className="absolute bottom-0 right-1/4 w-[500px] h-[500px] bg-violet-600/20 rounded-full blur-[120px] animate-pulse delay-700" />
       </div>

      <GlassCard className="w-full max-w-md p-10 relative z-10 backdrop-blur-2xl border-white/20">
        <div className="text-center mb-10">
          <div className="inline-flex items-center justify-center w-20 h-20 rounded-3xl bg-gradient-to-tr from-teal-400 to-cyan-600 mb-6 shadow-2xl shadow-cyan-500/40 transform rotate-3 hover:rotate-6 transition-transform">
            <Activity className="text-white w-10 h-10" />
          </div>
          <h1 className="text-4xl font-bold text-white mb-2 tracking-tight">MediAI</h1>
          <p className="text-cyan-200/60 font-light">Hệ thống Y tế Thông minh Thế hệ mới</p>
        </div>

        <form className="space-y-6" onSubmit={(e) => { e.preventDefault(); onLogin(); }}>
          <InputField icon={User} placeholder="Tên đăng nhập / Email" />
          <InputField icon={Shield} type="password" placeholder="Mật khẩu" />
          
          <Button type="submit" variant="primary" className="w-full text-lg !py-4 shadow-cyan-500/25">
            {isLogin ? 'Đăng nhập hệ thống' : 'Đăng ký tài khoản mới'}
          </Button>
        </form>

        <div className="mt-8 text-center border-t border-white/10 pt-6">
          <p className="text-slate-400 text-sm">
            {isLogin ? "Chưa có tài khoản?" : "Đã có tài khoản?"}
            <button 
              onClick={() => setIsLogin(!isLogin)}
              className="ml-2 text-cyan-300 hover:text-cyan-200 font-bold transition-colors underline decoration-dashed underline-offset-4"
            >
              {isLogin ? "Đăng ký ngay" : "Đăng nhập"}
            </button>
          </p>
        </div>
      </GlassCard>
    </div>
  );
};

const DoctorProfile = () => {
  return (
    <div className="animate-fadeIn space-y-8 pb-10">
       {/* Header Card */}
       <GlassCard className="relative overflow-hidden !p-0">
          {/* Cover */}
          <div className="h-48 bg-gradient-to-r from-teal-600 via-cyan-700 to-blue-800 relative">
             <div className="absolute inset-0 bg-black/20" />
             <div className="absolute bottom-0 left-0 w-full h-24 bg-gradient-to-t from-slate-900/80 to-transparent" />
          </div>
          <div className="px-8 pb-8">
             <div className="relative flex flex-col sm:flex-row justify-between items-end -mt-12 mb-6 gap-4">
                <div className="flex items-end gap-6">
                   <div className="w-32 h-32 rounded-full border-[6px] border-slate-950 bg-slate-800 flex items-center justify-center relative overflow-hidden shadow-2xl">
                      <User size={64} className="text-cyan-200" />
                   </div>
                   <div className="mb-2">
                      <h2 className="text-3xl font-bold text-white">BS. Minh Uyên</h2>
                      <p className="text-cyan-300 font-medium flex items-center gap-2 mt-1">
                        <Stethoscope size={16} /> Khoa Hồi sức tích cực (ICU)
                      </p>
                   </div>
                </div>
                <Button variant="primary" icon={FileText} className="hidden sm:flex shadow-cyan-500/20">Chỉnh sửa hồ sơ</Button>
             </div>

             {/* Stats Grid */}
             <div className="grid grid-cols-2 md:grid-cols-4 gap-4 border-t border-white/10 pt-6">
                {[
                  { label: 'Kinh nghiệm', value: '12 Năm', icon: Clock },
                  { label: 'Bệnh nhân', value: '1.5k+', icon: User },
                  { label: 'Đánh giá', value: '4.9/5', icon: Award },
                  { label: 'Ca trực', value: '24/7', icon: Calendar },
                ].map((s, i) => (
                  <div key={i} className="flex items-center gap-3 p-4 rounded-2xl bg-white/5 border border-white/5 hover:border-cyan-500/30 transition-all group">
                     <div className="p-2.5 bg-cyan-500/10 rounded-xl text-cyan-300 group-hover:scale-110 transition-transform"><s.icon size={20} /></div>
                     <div>
                       <p className="text-lg font-bold text-white">{s.value}</p>
                       <p className="text-xs text-slate-400 uppercase font-semibold tracking-wider">{s.label}</p>
                     </div>
                  </div>
                ))}
             </div>
          </div>
       </GlassCard>

       <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Column: Info */}
          <div className="space-y-6">
             <GlassCard className="p-6 space-y-6">
                <h3 className="text-lg font-bold text-white flex items-center gap-2 border-b border-white/10 pb-4">
                  <User size={20} className="text-cyan-400" /> Thông tin liên hệ
                </h3>
                <div className="space-y-5">
                   <div className="flex items-center gap-4 text-slate-300 group cursor-pointer hover:text-white transition-colors">
                      <div className="w-10 h-10 rounded-full bg-white/5 flex items-center justify-center text-cyan-400 border border-white/5 group-hover:border-cyan-400/30 transition-all"><Mail size={18} /></div>
                      <div>
                         <p className="text-xs text-slate-500 uppercase tracking-wide">Email</p>
                         <p className="font-medium">minhuyen.bs@mediai.vn</p>
                      </div>
                   </div>
                   <div className="flex items-center gap-4 text-slate-300 group cursor-pointer hover:text-white transition-colors">
                      <div className="w-10 h-10 rounded-full bg-white/5 flex items-center justify-center text-cyan-400 border border-white/5 group-hover:border-cyan-400/30 transition-all"><Phone size={18} /></div>
                      <div>
                         <p className="text-xs text-slate-500 uppercase tracking-wide">Hotline</p>
                         <p className="font-medium">+84 909 888 999</p>
                      </div>
                   </div>
                   <div className="flex items-center gap-4 text-slate-300 group cursor-pointer hover:text-white transition-colors">
                      <div className="w-10 h-10 rounded-full bg-white/5 flex items-center justify-center text-cyan-400 border border-white/5 group-hover:border-cyan-400/30 transition-all"><MapPin size={18} /></div>
                      <div>
                         <p className="text-xs text-slate-500 uppercase tracking-wide">Nơi làm việc</p>
                         <p className="font-medium">Bệnh viện Đa khoa Quốc tế</p>
                      </div>
                   </div>
                </div>
             </GlassCard>

             <GlassCard className="p-6">
                 <h3 className="text-lg font-bold text-white mb-6 flex items-center gap-2 border-b border-white/10 pb-4">
                   <GraduationCap size={20} className="text-cyan-400" /> Học vấn & Chứng chỉ
                 </h3>
                 <div className="space-y-6 relative pl-2">
                    {/* Timeline line */}
                    <div className="absolute left-[19px] top-2 bottom-2 w-0.5 bg-gradient-to-b from-cyan-500/50 to-transparent"></div>
                    {[
                      { year: '2010 - 2016', title: 'Bác sĩ Đa khoa', school: 'Đại học Y Dược TP.HCM' },
                      { year: '2016 - 2019', title: 'Thạc sĩ Nội khoa', school: 'Đại học Y Hà Nội' },
                      { year: '2020 - Nay', title: 'Chuyên khoa II Hồi sức', school: 'Đại học Y Dược TP.HCM' },
                    ].map((edu, i) => (
                       <div key={i} className="relative flex gap-4 group">
                          <div className="w-4 h-4 rounded-full bg-cyan-500 border-4 border-slate-900 mt-1.5 relative z-10 shrink-0 shadow-[0_0_10px_rgba(6,182,212,0.5)] group-hover:scale-125 transition-transform" />
                          <div>
                             <p className="text-xs text-cyan-300 font-mono mb-1 py-0.5 px-2 bg-cyan-500/10 rounded w-fit">{edu.year}</p>
                             <p className="font-bold text-white text-sm group-hover:text-cyan-200 transition-colors">{edu.title}</p>
                             <p className="text-sm text-slate-400">{edu.school}</p>
                          </div>
                       </div>
                    ))}
                 </div>
             </GlassCard>
          </div>

          {/* Right Column: Bio & Activities */}
          <div className="lg:col-span-2 space-y-6">
             <GlassCard className="p-8">
                <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                   <Activity size={20} className="text-cyan-400" /> Giới thiệu
                </h3>
                <p className="text-slate-300 leading-relaxed text-base">
                   Bác sĩ Minh Uyên là chuyên gia có hơn 12 năm kinh nghiệm trong lĩnh vực Hồi sức tích cực và Chống độc. 
                   Cô là người tiên phong trong việc ứng dụng <span className="text-cyan-300 font-bold">Trí tuệ nhân tạo (AI)</span> vào việc chẩn đoán sớm và điều trị cá thể hóa cho bệnh nhân nhiễm trùng huyết (Sepsis).
                   <br/><br/>
                   Với tâm niệm <span className="italic text-white">"Công nghệ vị nhân sinh"</span>, BS. Uyên không ngừng nghiên cứu để đưa MediAI trở thành trợ thủ đắc lực cho đội ngũ y bác sĩ, giúp giảm thiểu tỷ lệ tử vong và nâng cao chất lượng điều trị tại các bệnh viện tuyến đầu.
                </p>
             </GlassCard>

             <GlassCard className="p-6">
                <div className="flex justify-between items-center mb-6">
                   <h3 className="text-lg font-bold text-white flex items-center gap-2">
                     <Calendar size={20} className="text-cyan-400" /> Lịch làm việc tuần này
                   </h3>
                   <Button variant="secondary" className="!px-3 !py-1 !text-xs !rounded-lg">Quản lý lịch</Button>
                </div>
                <div className="grid grid-cols-7 gap-3">
                   {['T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'CN'].map((day, i) => {
                      const isActive = [0, 2, 4].includes(i); // Mock schedule
                      const isToday = i === 2; // Mock today is Wednesday
                      return (
                        <div key={i} className={`
                           rounded-2xl p-4 text-center border transition-all duration-300
                           ${isActive 
                             ? 'bg-gradient-to-br from-cyan-500/20 to-teal-500/10 border-cyan-500/30 shadow-lg shadow-cyan-500/10' 
                             : 'bg-white/5 border-white/5 opacity-50'
                           }
                           ${isToday ? 'ring-2 ring-cyan-400 ring-offset-2 ring-offset-slate-950' : ''}
                        `}>
                           <p className="text-xs text-slate-400 mb-2 uppercase font-bold">{day}</p>
                           {isActive ? (
                             <div className="space-y-1">
                                <div className="h-2 w-2 mx-auto rounded-full bg-cyan-400 shadow-[0_0_8px_rgba(34,211,238,1)]"></div>
                                <p className="text-[10px] text-cyan-300 font-bold mt-2">TRỰC</p>
                             </div>
                           ) : (
                             <p className="text-[10px] text-slate-600 font-medium py-1">Nghỉ</p>
                           )}
                        </div>
                      )
                   })}
                </div>
             </GlassCard>
          </div>
       </div>
    </div>
  )
}

const Sidebar = ({ currentPage, setPage, isMobile, isOpen, setIsOpen, onLogout }: any) => {
  const menuItems = [
    { id: 'dashboard', label: 'Tổng quan', icon: LayoutDashboard },
    { id: 'chatbot', label: 'Trợ lý AI', icon: MessageSquare },
    { id: 'predict_sepsis', label: 'Dự đoán Sepsis', icon: Droplet },
    { id: 'predict_mortality', label: 'Dự đoán Nguy cơ', icon: HeartPulse },
    { id: 'settings', label: 'Cài đặt', icon: Settings },
  ];

  const sidebarClasses = `
    fixed inset-y-0 left-0 z-50 w-80
    bg-slate-950/80 backdrop-blur-2xl border-r border-white/5
    transform transition-transform duration-500 cubic-bezier(0.4, 0, 0.2, 1)
    ${isMobile ? (isOpen ? 'translate-x-0' : '-translate-x-full') : 'translate-x-0'}
    flex flex-col
  `;

  return (
    <>
      {isMobile && isOpen && (
        <div 
          className="fixed inset-0 bg-black/80 z-40 backdrop-blur-sm"
          onClick={() => setIsOpen(false)}
        />
      )}
      
      <div className={sidebarClasses}>
        <div className="p-8 pb-4 flex items-center gap-4">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-teal-400 to-cyan-600 flex items-center justify-center shadow-lg shadow-cyan-500/20">
            <Activity className="text-white w-6 h-6" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-white tracking-tight">MediAI</h1>
            <div className="flex items-center gap-1.5 mt-0.5">
               <div className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
               <span className="text-[10px] font-bold text-emerald-400 uppercase tracking-widest">Online</span>
            </div>
          </div>
        </div>

        <div className="px-6 py-2">
           <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" size={14} />
              <input type="text" placeholder="Tìm kiếm..." className="w-full bg-white/5 border border-white/5 rounded-xl py-2 pl-9 pr-3 text-sm text-slate-300 focus:outline-none focus:bg-white/10 transition-colors" />
           </div>
        </div>

        <nav className="flex-1 px-4 py-6 space-y-1.5 overflow-y-auto custom-scrollbar">
          {menuItems.map((item) => {
            const isActive = currentPage === item.id;
            const Icon = item.icon;
            return (
              <button
                key={item.id}
                onClick={() => { setPage(item.id); if(isMobile) setIsOpen(false); }}
                className={`
                  w-full flex items-center gap-4 px-5 py-4 rounded-2xl transition-all duration-300 group relative overflow-hidden
                  ${isActive 
                    ? 'text-white' 
                    : 'text-slate-400 hover:text-white hover:bg-white/5'
                  }
                `}
              >
                {isActive && (
                  <div className="absolute inset-0 bg-gradient-to-r from-cyan-500/20 to-transparent border-l-4 border-cyan-400" />
                )}
                <Icon size={22} className={`${isActive ? 'text-cyan-300 drop-shadow-[0_0_8px_rgba(34,211,238,0.8)]' : 'group-hover:text-cyan-200 transition-colors'}`} />
                <span className="font-medium tracking-wide relative z-10">{item.label}</span>
              </button>
            );
          })}
        </nav>

        <div className="p-6 border-t border-white/5">
          <GlassCard 
            className={`
              !p-4 !bg-gradient-to-br !from-violet-600/20 !to-indigo-600/20 !border-white/5 mb-4 group cursor-pointer 
              hover:!border-cyan-400/30 transition-all
              ${currentPage === 'profile' ? '!border-cyan-400/50 !bg-violet-600/30' : ''}
            `}
            // Thêm sự kiện onClick để chuyển trang
            onClick={() => { setPage('profile'); if(isMobile) setIsOpen(false); }}
          >
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-white/10 flex items-center justify-center ring-2 ring-white/10 group-hover:ring-cyan-400/50 transition-all">
                <User size={18} className="text-white" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-bold text-white truncate group-hover:text-cyan-300 transition-colors">BS. Minh Uyên</p>
                <p className="text-xs text-cyan-200/60 truncate">Khoa Hồi sức tích cực</p>
              </div>
              <ChevronRight size={16} className="text-white/20 group-hover:text-cyan-400 group-hover:translate-x-1 transition-transform" />
            </div>
          </GlassCard>
          <button 
            onClick={onLogout}
            className="w-full flex items-center justify-center gap-2 px-4 py-2 rounded-xl text-rose-300/60 hover:text-rose-300 hover:bg-rose-500/10 transition-all text-sm font-medium"
          >
            <LogOut size={16} />
            Đăng xuất
          </button>
        </div>
      </div>
    </>
  );
};

const Dashboard = () => {
  const stats = [
    { title: 'Bệnh nhân', value: '1,248', change: '+12%', icon: User, color: 'from-blue-500 to-cyan-500', type: 'success' },
    { title: 'Nguy cơ cao', value: '24', change: '+2 new', icon: AlertTriangle, color: 'from-amber-500 to-orange-500', type: 'warning' },
    { title: 'Dự đoán Sepsis', value: '86', change: '-5%', icon: Droplet, color: 'from-rose-500 to-pink-500', type: 'danger' },
    { title: 'Độ chính xác AI', value: '98.5%', change: 'Stable', icon: Activity, color: 'from-emerald-500 to-teal-500', type: 'success' },
  ];

  return (
    <div className="space-y-8 animate-fadeIn">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-4">
        <div>
          <h2 className="text-3xl font-bold text-white mb-2">Tổng quan</h2>
          <p className="text-slate-400 flex items-center gap-2">
            Chào mừng trở lại, <span className="text-cyan-300 font-semibold">Bác sĩ Uyên</span>.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Button variant="secondary" className="!p-3 !rounded-xl relative">
            <Bell size={20} />
            <span className="absolute top-2 right-2 w-2 h-2 bg-rose-500 rounded-full animate-ping" />
            <span className="absolute top-2 right-2 w-2 h-2 bg-rose-500 rounded-full" />
          </Button>
          <GlassCard className="!py-2 !px-4 flex items-center gap-2 !rounded-xl">
             <Calendar size={16} className="text-cyan-400" />
             <span className="text-sm font-mono text-cyan-100">
               {new Date().toLocaleDateString('vi-VN', { weekday: 'short', day: '2-digit', month: '2-digit' })}
             </span>
          </GlassCard>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, index) => (
          <GlassCard key={index} hoverEffect className="group">
            <div className="flex justify-between items-start mb-6">
              <div className={`p-3.5 rounded-2xl bg-gradient-to-br ${stat.color} shadow-lg group-hover:scale-110 transition-transform duration-300`}>
                <stat.icon size={22} className="text-white" />
              </div>
              <Badge type={stat.type as any}>{stat.change}</Badge>
            </div>
            <h3 className="text-3xl font-bold text-white mb-1 tracking-tight">{stat.value}</h3>
            <p className="text-slate-400 text-sm font-medium">{stat.title}</p>
          </GlassCard>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <GlassCard className="lg:col-span-2 min-h-[400px] flex flex-col">
          <div className="flex justify-between items-center mb-8">
            <h3 className="text-xl font-bold text-white flex items-center gap-3">
              <Activity size={24} className="text-cyan-400" />
              Phân tích xu hướng
            </h3>
            <div className="flex gap-2">
               {['Ngày', 'Tuần', 'Tháng'].map(t => (
                 <button key={t} className="px-3 py-1 rounded-lg text-xs font-medium bg-white/5 hover:bg-white/10 text-slate-300 transition-colors border border-white/5">{t}</button>
               ))}
            </div>
          </div>
          
          {/* Enhanced Chart Mockup */}
          <div className="flex-1 flex items-end justify-between gap-4 px-4 pb-4 relative">
            {/* Grid Lines */}
            <div className="absolute inset-0 flex flex-col justify-between pointer-events-none opacity-20">
               <div className="border-t border-dashed border-white"></div>
               <div className="border-t border-dashed border-white"></div>
               <div className="border-t border-dashed border-white"></div>
               <div className="border-t border-dashed border-white"></div>
            </div>
            
            {[45, 60, 35, 75, 50, 85, 65, 90, 70, 55, 80, 60].map((h, i) => (
              <div key={i} className="flex-1 flex flex-col justify-end group h-full z-10">
                 <div className="w-full relative rounded-t-lg overflow-hidden transition-all duration-500 hover:opacity-100 opacity-80" style={{ height: `${h}%` }}>
                    <div className="absolute inset-0 bg-gradient-to-t from-cyan-600/60 to-teal-400/60 group-hover:from-cyan-500 group-hover:to-teal-300"></div>
                 </div>
                 <div className="h-1 w-full mt-2 bg-white/5 rounded-full"></div>
              </div>
            ))}
          </div>
        </GlassCard>

        <GlassCard>
          <h3 className="text-xl font-bold text-white mb-6">Bệnh án gần đây</h3>
          <div className="space-y-4">
            {[1, 2, 3, 4].map((_, i) => (
              <div key={i} className="group flex items-center gap-4 p-4 rounded-2xl bg-white/5 border border-white/5 hover:bg-white/10 hover:border-cyan-500/30 transition-all cursor-pointer">
                <div className="w-12 h-12 rounded-full bg-gradient-to-br from-slate-700 to-slate-800 flex items-center justify-center text-cyan-300 font-bold text-sm border border-white/10 group-hover:scale-105 transition-transform">
                  BN
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-bold text-white truncate group-hover:text-cyan-200 transition-colors">Nguyễn Văn A</p>
                  <p className="text-xs text-slate-400 mt-1">Sepsis Risk: <span className="text-emerald-400 font-bold">Thấp</span></p>
                </div>
                <ChevronRight size={18} className="text-slate-600 group-hover:text-cyan-400 group-hover:translate-x-1 transition-all" />
              </div>
            ))}
          </div>
          <Button variant="ghost" className="w-full mt-6 text-sm border border-white/10">Xem toàn bộ danh sách</Button>
        </GlassCard>
      </div>
    </div>
  );
};

const Chatbot = () => {
  const [messages, setMessages] = useState<Message[]>(MOCK_CHAT_HISTORY);
  const [input, setInput] = useState('');
  const chatEndRef = useRef<HTMLDivElement>(null);

  const handleSend = () => {
    if (!input.trim()) return;
    const userMsg: Message = { id: Date.now().toString(), text: input, sender: 'user', timestamp: new Date() };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setTimeout(() => {
      const botMsg: Message = { 
        id: (Date.now() + 1).toString(), 
        text: "Hệ thống đang tra cứu cơ sở dữ liệu và phân tích...", 
        sender: 'bot', 
        timestamp: new Date() 
      };
      setMessages(prev => [...prev, botMsg]);
    }, 1000);
  };

  return (
    <div className="h-[calc(100vh-8rem)] flex flex-col gap-6 animate-fadeIn">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-white">Trợ lý MediAI</h2>
          <p className="text-slate-400">Hỗ trợ chẩn đoán và tra cứu phác đồ điều trị</p>
        </div>
        <Button variant="secondary" className="!px-4 !py-2 !text-sm">
           <FileText size={16} /> Xuất báo cáo
        </Button>
      </div>

      <GlassCard className="flex-1 flex flex-col min-h-0 !p-0 overflow-hidden backdrop-blur-3xl">
        <div className="flex-1 overflow-y-auto p-8 space-y-8 custom-scrollbar scroll-smooth">
          {messages.map((msg) => (
            <div key={msg.id} className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`
                max-w-[80%] lg:max-w-[70%] p-6 rounded-3xl relative shadow-xl backdrop-blur-sm
                ${msg.sender === 'user' 
                  ? 'bg-gradient-to-br from-cyan-600 to-blue-600 text-white rounded-tr-sm' 
                  : 'bg-white/10 text-slate-100 border border-white/10 rounded-tl-sm'
                }
              `}>
                <div className="flex items-start gap-4">
                  {msg.sender === 'bot' && (
                     <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-teal-400 to-cyan-500 flex-shrink-0 flex items-center justify-center shadow-lg shadow-cyan-500/30">
                       <Bot size={16} className="text-white" />
                     </div>
                  )}
                  <div className="flex-1">
                    <p className="leading-relaxed text-[15px]">{msg.text}</p>
                    <span className="text-[11px] opacity-60 mt-3 block font-medium">
                      {msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          ))}
          <div ref={chatEndRef} />
        </div>

        <div className="p-6 border-t border-white/10 bg-black/20">
          <div className="relative flex gap-4 max-w-5xl mx-auto">
             <Button variant="secondary" className="!px-4 !rounded-2xl">
               <FileText size={20} />
             </Button>
             <div className="flex-1 relative">
                <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                    placeholder="Nhập triệu chứng hoặc câu hỏi y khoa..."
                    className="w-full bg-white/5 border border-white/10 rounded-2xl py-3.5 pl-5 pr-12 text-white placeholder-slate-500 focus:outline-none focus:bg-white/10 focus:border-cyan-500/50 transition-all shadow-inner"
                />
             </div>
             <Button onClick={handleSend} variant="primary" className="!px-6 !rounded-2xl">
               <Send size={20} />
             </Button>
          </div>
        </div>
      </GlassCard>
    </div>
  );
};

const PredictionForm = ({ type }: { type: 'sepsis' | 'mortality' }) => {
  const inputs = type === 'sepsis' ? SEPSIS_INPUTS : MORTALITY_INPUTS;
  const title = type === 'sepsis' ? 'Dự đoán Sepsis' : 'Dự đoán Nguy cơ Tử vong';
  const accentGradient = type === 'sepsis' ? 'from-teal-400 to-cyan-500' : 'from-rose-500 to-orange-500';

  return (
    <div className="animate-fadeIn max-w-5xl mx-auto pb-10">
      <div className="mb-10 text-center">
        <h2 className="text-4xl font-bold text-white mb-3 tracking-tight">{title}</h2>
        <p className="text-slate-400 max-w-2xl mx-auto">Nhập các chỉ số lâm sàng và cận lâm sàng để hệ thống AI phân tích và đưa ra cảnh báo sớm.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        <GlassCard className="lg:col-span-8 p-8 relative overflow-visible">
          <div className={`absolute top-0 left-0 w-full h-1 bg-gradient-to-r ${accentGradient} opacity-50`}></div>
          
          <h3 className="text-xl font-bold text-white mb-8 flex items-center gap-3">
             <div className={`w-8 h-8 rounded-lg bg-gradient-to-br ${accentGradient} flex items-center justify-center`}>
                <Activity size={16} className="text-white" />
             </div>
             Thông tin lâm sàng
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-x-6 gap-y-8">
            {inputs.map((input) => (
              <InputField 
                key={input.id} 
                label={input.label} 
                icon={input.icon} 
                unit={input.unit} 
                placeholder="---"
                type="number"
              />
            ))}
          </div>

          <div className="mt-10 pt-8 border-t border-white/10 flex justify-end gap-4">
            <Button variant="secondary" className="!bg-transparent border-white/20">Reset</Button>
            <Button variant="primary" className="px-8 shadow-2xl shadow-cyan-500/20">
              <Activity className="animate-pulse" size={20} /> 
              Phân tích Dữ liệu
            </Button>
          </div>
        </GlassCard>

        {/* Prediction Sidebar */}
        <div className="lg:col-span-4 space-y-6">
           <GlassCard className="p-8 text-center relative overflow-hidden group">
             <div className="absolute inset-0 bg-gradient-to-b from-cyan-500/5 to-transparent pointer-events-none" />
             <h3 className="text-lg font-bold text-slate-300 mb-6 uppercase tracking-widest text-xs">Kết quả dự báo</h3>
             
             <div className="relative w-48 h-48 mx-auto mb-6 flex items-center justify-center">
               {/* Animated Rings */}
               <div className="absolute inset-0 rounded-full border-8 border-slate-800" />
               <div className="absolute inset-0 rounded-full border-8 border-t-cyan-400 border-r-cyan-400/50 border-b-transparent border-l-transparent rotate-[45deg] animate-spin duration-[3s]" />
               <div className="absolute inset-2 rounded-full border-2 border-white/5" />
               
               <div className="flex flex-col items-center z-10">
                 <span className="text-5xl font-black text-white tracking-tighter">--</span>
                 <span className="text-sm text-cyan-400 font-bold uppercase mt-1">% Nguy cơ</span>
               </div>
             </div>
             
             <p className="text-slate-500 text-sm">Chưa có dữ liệu đầu vào.</p>
           </GlassCard>

           <GlassCard className="p-6 !bg-gradient-to-br !from-amber-500/10 !to-orange-500/5 !border-amber-500/20">
             <h3 className="text-sm font-bold text-amber-200 mb-3 flex items-center gap-2">
               <AlertTriangle size={16} /> Lưu ý quan trọng
             </h3>
             <p className="text-xs text-slate-300 leading-relaxed opacity-80">
               Hệ thống AI chỉ hỗ trợ ra quyết định. Bác sĩ cần kiểm tra lại các chỉ số sinh tồn và tiền sử bệnh nhân trước khi đưa ra phác đồ điều trị cuối cùng.
             </p>
           </GlassCard>
        </div>
      </div>
    </div>
  );
};

// --- Main App ---

export default function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [currentPage, setCurrentPage] = useState<Page>('dashboard');
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [isMobile, setIsMobile] = useState(false);

  useEffect(() => {
    const checkResize = () => setIsMobile(window.innerWidth < 1024);
    checkResize();
    window.addEventListener('resize', checkResize);
    return () => window.removeEventListener('resize', checkResize);
  }, []);

  if (!isLoggedIn) return <AuthPage onLogin={() => setIsLoggedIn(true)} />;

  const renderContent = () => {
    switch (currentPage) {
      case 'dashboard': return <Dashboard />;
      case 'chatbot': return <Chatbot />;
      case 'predict_sepsis': return <PredictionForm type="sepsis" />;
      case 'predict_mortality': return <PredictionForm type="mortality" />;
      case 'profile': return <DoctorProfile />; // Thêm case hiển thị profile
      case 'settings': 
        return (
          <GlassCard className="p-10 max-w-3xl mx-auto animate-fadeIn">
            <h2 className="text-3xl font-bold text-white mb-8">Cài đặt hệ thống</h2>
            <div className="space-y-6">
               {[
                 { title: 'Chế độ tối (Dark Mode)', desc: 'Tối ưu hóa cho môi trường bệnh viện thiếu sáng', active: true },
                 { title: 'Thông báo đẩy', desc: 'Nhận cảnh báo khi có bệnh nhân nguy kịch', active: true },
                 { title: 'Xác thực 2 lớp (2FA)', desc: 'Bảo mật tài khoản bác sĩ', active: false }
               ].map((setting, i) => (
                 <div key={i} className="flex items-center justify-between p-5 rounded-2xl bg-white/5 border border-white/5 hover:border-white/10 transition-all">
                   <div>
                     <h3 className="text-white font-bold text-lg">{setting.title}</h3>
                     <p className="text-sm text-slate-400 mt-1">{setting.desc}</p>
                   </div>
                   <div className={`w-14 h-7 rounded-full relative cursor-pointer transition-colors ${setting.active ? 'bg-cyan-500' : 'bg-slate-700'}`}>
                     <div className={`absolute top-1 w-5 h-5 bg-white rounded-full shadow-md transition-all ${setting.active ? 'right-1' : 'left-1'}`} />
                   </div>
                 </div>
               ))}
            </div>
          </GlassCard>
        );
      default: return <Dashboard />;
    }
  };

  return (
    <div className={`min-h-screen ${THEME.colors.bg} text-slate-50 font-sans selection:bg-cyan-500/30 overflow-x-hidden`}>
      {/* Background Ambience */}
      <div className="fixed inset-0 z-0 pointer-events-none">
         <div className="absolute top-[-20%] left-[-10%] w-[70vw] h-[70vw] bg-teal-900/10 rounded-full blur-[150px] animate-pulse-slow" />
         <div className="absolute bottom-[-20%] right-[-10%] w-[60vw] h-[60vw] bg-indigo-900/20 rounded-full blur-[150px]" />
         {/* Grid overlay */}
         <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-[0.02] mix-blend-overlay"></div>
      </div>

      <Sidebar 
        currentPage={currentPage} 
        setPage={setCurrentPage} 
        isMobile={isMobile}
        isOpen={isSidebarOpen}
        setIsOpen={setIsSidebarOpen}
        onLogout={() => setIsLoggedIn(false)}
      />

      <main className={`relative z-10 transition-all duration-500 min-h-screen ${isMobile ? 'pl-0' : 'pl-80'}`}>
        {isMobile && (
          <div className="sticky top-0 z-30 px-4 py-3 flex items-center justify-between bg-slate-950/80 backdrop-blur-xl border-b border-white/10">
             <div className="flex items-center gap-2">
               <Activity size={20} className="text-cyan-400" />
               <span className="font-bold text-lg text-white">MediAI</span>
             </div>
             <button onClick={() => setIsSidebarOpen(true)} className="p-2 rounded-xl bg-white/5 text-white">
               <Menu size={24} />
             </button>
          </div>
        )}
        <div className="p-6 lg:p-10 max-w-[1600px] mx-auto">
          {renderContent()}
        </div>
      </main>

      <style>{`
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(15px) scale(0.98); }
          to { opacity: 1; transform: translateY(0) scale(1); }
        }
        .animate-fadeIn { animation: fadeIn 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards; }
        
        .custom-scrollbar::-webkit-scrollbar { width: 6px; }
        .custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
        .custom-scrollbar::-webkit-scrollbar-thumb { background: rgba(255, 255, 255, 0.1); border-radius: 10px; }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover { background: rgba(255, 255, 255, 0.2); }
      `}</style>
    </div>
  );
}