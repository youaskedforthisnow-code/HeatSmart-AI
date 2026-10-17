import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import StringIO
from datetime import datetime

st.set_page_config(page_title="HeatSmart AI", page_icon="🔥", layout="wide")

st.markdown("""
<style>
.block-container {padding-top: 1.6rem; padding-bottom: 2rem; max-width: 1250px;}
.hero {padding: 1.4rem 1.6rem; border-radius: 18px; background: linear-gradient(120deg,#10243a,#176b73); color:white; margin-bottom:1rem;}
.hero h1 {color:white; margin-bottom:.2rem;}
.small-note {font-size: .9rem; color: #687386;}
div[data-testid="stMetric"] {border:1px solid rgba(120,130,145,.25); padding: .8rem; border-radius: 12px;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="hero"><h1>🔥 HeatSmart AI</h1><div>Intelligent Heat Treatment Analysis Platform</div><p>منصة تعليمية لتحليل معاملات المعالجة الحرارية للفولاذ</p></div>', unsafe_allow_html=True)

with st.sidebar:
    st.header("القائمة الرئيسية")
    page = st.radio("انتقلي إلى", ["لوحة التحكم", "تحليل المعاملة", "مقارنة الحالات", "تحليل البيانات CSV", "دليل علمي", "عن المشروع"])
    st.divider()
    st.caption("نسخة أولية قابلة للتشغيل — النتائج التوضيحية ليست بديلاً عن القياسات المختبرية.")

st.warning("تنبيه علمي: وضع العرض يستخدم بيانات/علاقات توضيحية فقط، وليس نموذجاً تجريبياً موثّقاً. لا تستخدمي نتائجه لاتخاذ قرارات صناعية. للحصول على تنبؤ حقيقي، حمّلي بيانات موثوقة خاصة بدرجة الفولاذ نفسها.")

def demo_estimate(steel, aust, hold, medium, temper, temper_time):
    # Explicitly illustrative heuristic, not a validated metallurgical model.
    medium_factor = {"ماء": 1.00, "زيت": 0.82, "هواء": 0.58, "غير معروف": 0.70}[medium]
    grade_factor = {"AISI 1045": 1.00, "AISI 4140": 1.10, "AISI 4340": 1.14, "فولاذ غير محدد": 0.90}[steel]
    base = 18 + max(0, aust - 700) * 0.10 + min(max(hold, 0), 120) * 0.035
    quench = medium_factor * grade_factor * max(0, (aust - 650) / 3.5)
    temper_softening = max(0, temper - 150) * 0.045 + max(0, temper_time - 0.5) * 1.3
    estimate = np.clip(base + quench - temper_softening, 8, 67)
    return float(estimate)

def sample_data():
    return pd.DataFrame({
        "steel_grade": ["AISI 1045","AISI 1045","AISI 4140","AISI 4140","AISI 4340","AISI 1045","AISI 4140","AISI 4340"],
        "austenitizing_temp_C": [820,840,850,860,850,830,870,860],
        "holding_time_min": [20,30,25,35,30,25,40,35],
        "cooling_medium": ["water","oil","oil","water","oil","air","oil","water"],
        "tempering_temp_C": [200,300,250,400,350,250,300,450],
        "tempering_time_h": [1,1,1.5,2,1,1,2,2],
        "hardness_HRC": [np.nan]*8
    })

if page == "لوحة التحكم":
    st.subheader("مرحباً بك في HeatSmart AI")
    st.write("واجهة أولية لمشروع جامعي في المعاملات الحرارية. ابدئي بتحليل حالة، أو قارني ظروفاً مختلفة، أو ارفعي بيانات مختبرية لبناء نموذج تنبؤ.")
    c1,c2,c3 = st.columns(3)
    c1.metric("وحدات المنصة", "6")
    c2.metric("طرق الإدخال", "يدوي / CSV")
    c3.metric("نوع النسخة", "Prototype")
    st.markdown("### مسار العمل المقترح")
    st.markdown("1. حددي درجة الفولاذ وظروف المعاملة الحرارية.\n2. استخدمي وضع العرض لفهم الواجهة فقط.\n3. اجمعي بيانات موثوقة من مختبر أو ورقة علمية.\n4. ارفعي البيانات في قسم تحليل CSV لتقييم إمكانية تدريب نموذج.\n5. اشرحي الافتراضات والحدود العلمية في المناقشة.")
    st.info("للعرض الأكاديمي، من الأفضل تسمية القيمة الحالية «تقدير توضيحي» إلى أن يتم استبدالها بنموذج مدرّب ومختبَر على بيانات موثقة.")

elif page == "تحليل المعاملة":
    st.subheader("تحليل ظروف المعالجة الحرارية")
    left,right = st.columns([1,1])
    with left:
        steel = st.selectbox("درجة الفولاذ", ["AISI 1045","AISI 4140","AISI 4340","فولاذ غير محدد"])
        aust = st.slider("درجة حرارة الأوستنة (°C)", 700, 1000, 850, 5)
        hold = st.slider("زمن التثبيت (دقيقة)", 5, 120, 30, 5)
        medium = st.selectbox("وسط التبريد", ["ماء","زيت","هواء","غير معروف"])
        temper = st.slider("درجة حرارة المراجعة Tempering (°C)", 100, 700, 300, 10)
        temper_time = st.slider("زمن المراجعة (ساعة)", 0.5, 8.0, 1.0, 0.5)
        run = st.button("حلّل الحالة", type="primary", use_container_width=True)
    with right:
        st.markdown("#### ملخص الحالة")
        st.write(f"**الفولاذ:** {steel}")
        st.write(f"**الأوستنة:** {aust} °C لمدة {hold} دقيقة")
        st.write(f"**التبريد:** {medium}")
        st.write(f"**المراجعة:** {temper} °C لمدة {temper_time} ساعة")
        st.caption("التفسير التالي نوعي وتعليمي؛ سلوك الفولاذ يعتمد على التركيب الكيميائي والهندسة ومعدل التبريد الفعلي.")
        if run:
            value = demo_estimate(steel, aust, hold, medium, temper, temper_time)
            st.metric("قيمة صلادة توضيحية", f"{value:.1f} HRC")
            st.warning("هذه القيمة مولّدة بمعادلة توضيحية مصطنعة وليست تنبؤاً هندسياً صالحاً للاستخدام. استبدليها بنتيجة نموذج مدرّب على بيانات موثقة قبل تقديمها كتنبؤ.")
            if medium == "ماء":
                st.write("**ملاحظة نوعية:** التبريد بالماء قد يحقق معدل تبريد أعلى، لكنه قد يزيد مخاطر الإجهادات والتشقق لبعض الأشكال والدرجات.")
            elif medium == "زيت":
                st.write("**ملاحظة نوعية:** الزيت عادةً أبطأ من الماء، وقد يقلل بعض مخاطر التشوه، لكن النتيجة تعتمد على نوع الزيت وظروف التبريد.")
            else:
                st.write("**ملاحظة نوعية:** التبريد بالهواء غالباً أبطأ، لكن الاستجابة تعتمد بشدة على قابلية التصلد وسمك القطعة.")
            st.markdown("**الخطوة التالية:** قارني النتيجة بقياس HRC/HV موثق لنفس درجة الفولاذ وظروف المعالجة.")

elif page == "مقارنة الحالات":
    st.subheader("مقارنة ظروف المعالجة")
    st.write("غيّري القيم أدناه لمقارنة تأثير الإعدادات داخل النموذج التوضيحي فقط.")
    steel = st.selectbox("درجة الفولاذ للمقارنة", ["AISI 1045","AISI 4140","AISI 4340"], key="cmpsteel")
    austs = st.multiselect("درجات الأوستنة (°C)", [760,780,800,820,840,860,880,900,920], default=[800,840,880])
    medium = st.selectbox("وسط التبريد", ["ماء","زيت","هواء"], key="cmpmedium")
    temper = st.slider("درجة المراجعة (°C)", 100, 700, 300, 10, key="cmptemper")
    hold = st.slider("زمن التثبيت (دقيقة)", 5, 120, 30, 5, key="cmphold")
    if austs:
        rows=[]
        for t in austs:
            rows.append({"Austenitizing (°C)":t, "Illustrative hardness (HRC)":demo_estimate(steel,t,hold,medium,temper,1.0)})
        df=pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True, hide_index=True)
        fig,ax=plt.subplots()
        ax.plot(df["Austenitizing (°C)"],df["Illustrative hardness (HRC)"],marker="o")
        ax.set_xlabel("Austenitizing temperature (°C)")
        ax.set_ylabel("Illustrative value (HRC)")
        ax.set_title("Illustrative comparison — not experimental")
        ax.grid(True, alpha=.3)
        st.pyplot(fig)
        st.download_button("تنزيل المقارنة CSV", df.to_csv(index=False).encode("utf-8-sig"), "heatsmart_comparison.csv", "text/csv")
    else:
        st.info("اختاري درجة حرارة واحدة على الأقل.")

elif page == "تحليل البيانات CSV":
    st.subheader("رفع بيانات وتجربة نموذج انحدار")
    st.markdown("الأعمدة المطلوبة: `austenitizing_temp_C`, `holding_time_min`, `tempering_temp_C`, `tempering_time_h`, `hardness_HRC`. يمكن إضافة `cooling_medium` و`steel_grade`.")
    uploaded = st.file_uploader("ارفعي ملف CSV", type=["csv"])
    st.caption("للتدريب العلمي، يجب أن تكون كل صفوف البيانات قياسات موثقة، وأن تكون الوحدات ودرجة الفولاذ معروفة.")
    if uploaded:
        try:
            df = pd.read_csv(uploaded)
            st.write("معاينة البيانات")
            st.dataframe(df.head(20), use_container_width=True)
            required = ["austenitizing_temp_C","holding_time_min","tempering_temp_C","tempering_time_h","hardness_HRC"]
            missing = [c for c in required if c not in df.columns]
            if missing:
                st.error("الأعمدة الناقصة: " + ", ".join(missing))
            else:
                usable = df[required].apply(pd.to_numeric, errors="coerce").dropna()
                st.write(f"عدد الصفوف الكاملة الصالحة: **{len(usable)}** من {len(df)}")
                if len(usable) >= 8:
                    try:
                        from sklearn.model_selection import train_test_split
                        from sklearn.ensemble import RandomForestRegressor
                        from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
                        X=usable[required[:-1]]
                        y=usable["hardness_HRC"]
                        test_size=0.25 if len(usable)>=12 else 0.33
                        X_train,X_test,y_train,y_test=train_test_split(X,y,test_size=test_size,random_state=42)
                        model=RandomForestRegressor(n_estimators=200, random_state=42)
                        model.fit(X_train,y_train)
                        pred=model.predict(X_test)
                        a,b,c=st.columns(3)
                        a.metric("MAE", f"{mean_absolute_error(y_test,pred):.2f} HRC")
                        b.metric("RMSE", f"{np.sqrt(mean_squared_error(y_test,pred)):.2f} HRC")
                        r2=r2_score(y_test,pred) if len(y_test)>1 else np.nan
                        c.metric("R²", f"{r2:.3f}" if np.isfinite(r2) else "غير متاح")
                        st.dataframe(pd.DataFrame({"Measured HRC":y_test.values,"Predicted HRC":pred}), use_container_width=True)
                        st.warning("هذه مقاييس اختبار على عينة صغيرة وقد تكون غير مستقرة. يجب منع تسرب البيانات، وفصل العينات بحسب الدفعات/التركيبات عند الحاجة، والتحقق على بيانات مستقلة قبل ادعاء الدقة.")
                    except Exception as e:
                        st.error(f"تعذر تدريب النموذج: {e}")
                else:
                    st.info("توجد بيانات قليلة جداً للتدريب التجريبي (نحتاج 8 صفوف كاملة على الأقل في هذه النسخة). اجمعي بيانات أكثر، ويفضل عشرات أو مئات القياسات الموثقة.")
                st.download_button("تنزيل البيانات بعد التنظيف", usable.to_csv(index=False).encode("utf-8-sig"), "heatsmart_clean_data.csv", "text/csv")
        except Exception as e:
            st.error(f"تعذر قراءة الملف: {e}")
    else:
        st.info("ما عندج بيانات مختبرية حالياً؟ نزّلي قالب CSV واملئيه بقياسات حقيقية قبل التدريب.")
        template = pd.DataFrame(columns=["steel_grade","austenitizing_temp_C","holding_time_min","cooling_medium","tempering_temp_C","tempering_time_h","hardness_HRC"])
        st.download_button("تنزيل قالب CSV فارغ", template.to_csv(index=False).encode("utf-8-sig"), "heatsmart_template.csv", "text/csv")
        st.write("مثال توضيحي لشكل الجدول فقط (قيم الصلادة فارغة عمداً):")
        st.dataframe(sample_data(), use_container_width=True, hide_index=True)

elif page == "دليل علمي":
    st.subheader("دليل مختصر للمعاملات الحرارية")
    with st.expander("الأوستنة Austenitizing", expanded=True):
        st.write("تسخين الفولاذ إلى مجال حراري مناسب لتكوين الأوستنايت. درجة الحرارة المناسبة تعتمد على تركيب الفولاذ ونوعه، ولا توجد قيمة واحدة مناسبة لكل الدرجات.")
    with st.expander("التبريد السريع Quenching"):
        st.write("التبريد السريع قد يحول الأوستنايت إلى مارتنسايت في الفولاذ القابل للتصلد. معدل التبريد الفعلي يتأثر بوسط التبريد، شكل القطعة، أبعادها، والتحريك.")
    with st.expander("المراجعة Tempering"):
        st.write("تسخين الفولاذ المقسّى إلى درجة أقل من المجال الحرج ثم تثبيته والتبريد. غالباً يقلل الهشاشة والإجهادات ويغيّر الصلادة والمتانة. العلاقة ليست عامة وثابتة لكل فولاذ.")
    with st.expander("مخططات TTT وCCT"):
        st.write("توضح مخططات TTT التحولات عند درجة حرارة ثابتة، بينما توضح مخططات CCT التحولات أثناء التبريد المستمر. يجب استخدام مخطط خاص بالتركيب الكيميائي وحالة المادة.")
    with st.expander("مراجع أولية للبحث"):
        st.markdown("- ASM Handbook, Volume 4A: Steel Heat Treating Fundamentals and Processes.\n- George Krauss, *Steels: Processing, Structure, and Performance*.\n- ابحثي عن بيانات مفتوحة ومقالات محكّمة لدرجة الفولاذ المحددة، وتأكدي من أن البيانات تشمل ظروف المعالجة والصلادة المقاسة.")
    st.info("أضيفي مراجع محددة مع بيانات النشر/DOI إلى التقرير النهائي بعد التأكد من أنها تدعم نوع الفولاذ والنتيجة المستخدمة.")

elif page == "عن المشروع":
    st.subheader("عن HeatSmart AI")
    st.write("HeatSmart AI نموذج أولي تعليمي يوضح كيف يمكن دمج واجهة تفاعلية، رسوم بيانية، ورفع بيانات معاملة حرارية في منصة هندسية.")
    st.markdown("""
**حدود النسخة الحالية**
- القيمة في صفحة تحليل المعاملة توضيحية وليست تنبؤاً علمياً موثّقاً.
- التدريب يتطلب ملف CSV يحتوي قياسات صلادة حقيقية ووحدات واضحة.
- النتائج لا تصلح لاتخاذ قرارات تصنيع أو سلامة.
- الصور المجهرية وتحليل الشقوق ليست ضمن وظائف النسخة الأولى.
""")
    report = f"""# HeatSmart AI — ملخص المشروع
تاريخ إنشاء الملخص: {datetime.now().strftime('%Y-%m-%d')}

## الهدف
منصة تعليمية لتحليل متغيرات المعالجة الحرارية للفولاذ ودراسة علاقتها بالصلادة.

## الوظائف
- إدخال ظروف الأوستنة والتبريد والمراجعة.
- مقارنة عدة درجات حرارة وعرض مخطط.
- رفع بيانات CSV وتدريب نموذج انحدار تجريبي عند توفر بيانات كافية.
- شرح مفاهيم المعالجة الحرارية وحدود النموذج.

## تحذير علمي
قيم وضع العرض توضيحية وليست قياسات مختبرية أو تنبؤات معتمدة. لا يجوز ادعاء دقة علمية قبل التدريب والتحقق ببيانات موثوقة ومستقلة.

## خطة تطوير
1. اختيار درجة فولاذ محددة.
2. جمع بيانات موثقة تشمل المعالجة والصلادة.
3. توثيق المصدر والوحدات.
4. تدريب النموذج وتقييمه والتحقق من التعميم.
5. مقارنة النتائج بقياسات مستقلة.
"""
    st.download_button("تنزيل ملخص المشروع Markdown", report, "HeatSmart_AI_project_report.md", "text/markdown")

st.divider()
st.caption("HeatSmart AI • University prototype • Educational use only")
