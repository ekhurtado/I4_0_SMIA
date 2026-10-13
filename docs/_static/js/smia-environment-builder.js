/**
 * SMIA Environment Builder
 * Client-side logic for generating docker-compose and configuration files.
 * v3.4 — accept=".aasx" filters, brand-primary colour tokens in SVGs,
 *         full-width Assets summary card with Plan / Assets sub-sections
 */

document.addEventListener("DOMContentLoaded", () => {
    if (document.getElementById("smia-builder-root")) {
        SMIA_Builder.init();
    }
});

/* ============================================================
   EMBEDDED SVG ICONS
   ============================================================ */
const ICONS = {

    // ── Environment selection cards (Step 1 main grid) ─────────

    // Modern Python local development: terminal window with Python snake motif
    // local: `<svg width="46" height="46" viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" data-iconid="373336" data-svgname="Python"><defs id="element_79bbdd3e"><linearGradient id="a" x1="-132.23" y1="235.872" x2="-132.18" y2="235.822" gradientTransform="matrix(189.38, 0, 0, -189.81, 25054.681, 44783.902)" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#387eb8" id="element_f0655dd2"></stop><stop offset="1" stop-color="#366994" id="element_cc2d510c"></stop></linearGradient><linearGradient id="b" x1="-132.549" y1="236.178" x2="-132.492" y2="236.128" gradientTransform="matrix(189.38, 0, 0, -189.81, 25120.681, 44848.152)" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#ffe052" id="element_3a782c9d"></stop><stop offset="1" stop-color="#ffc331" id="element_cfcb6247"></stop></linearGradient></defs><title id="element_bee1ed1b">folder_type_python</title><path d="M27.4,5.5H18.1L16,9.7H4.3V26.5H29.5V5.5Zm0,4.2H19.2l1.1-2.1h7.1Z" style="fill: #74beef" id="element_7f7eefc6"></path><path d="M20.918,11.009c-5.072,0-4.751,2.206-4.751,2.206v2.293H20.99v.719H14.246S11,15.825,11,21s2.866,4.968,2.866,4.968h1.655V23.556a2.721,2.721,0,0,1,2.786-2.884h4.83a2.583,2.583,0,0,0,2.694-2.626V13.668S26.24,11,20.944,11h0Zm-2.666,1.536a.872.872,0,1,1-.845.894h0v-.014a.87.87,0,0,1,.867-.873h0Z" style="fill:url(#a)" id="element_4d325208"></path><path d="M21.061,31c5.071,0,4.75-2.214,4.75-2.214V26.5H20.989V25.78h6.765S31,26.145,31,21s-2.866-4.968-2.866-4.968H26.457v2.384A2.721,2.721,0,0,1,23.671,21.3H18.839a2.586,2.586,0,0,0-2.7,2.627v4.408S15.734,31,21.03,31h.031Zm2.665-1.544a.872.872,0,1,1,.845-.894h0v.022a.869.869,0,0,1-.867.872h.022Z" style="fill:url(#b)" id="element_a1f37a1f"></path></svg>`,
    local: `<img src="_static/images/environment_builder_images/python_folder_horizontal_icon.ico" width="46" height="46" alt="Python icon" />`,

    // Official-style Docker logo (brand blue kept as Docker brand colour)
    docker: `<svg viewBox="0 0 756.26 596.9" width="40" height="40"><path fill="#1d63ed" d="M743.96,245.25c-18.54-12.48-67.26-17.81-102.68-8.27-1.91-35.28-20.1-65.01-53.38-90.95l-12.32-8.27-8.21,12.4c-16.14,24.5-22.94,57.14-20.53,86.81,1.9,18.28,8.26,38.83,20.53,53.74-46.1,26.74-88.59,20.67-276.77,20.67H.06c-.85,42.49,5.98,124.23,57.96,190.77,5.74,7.35,12.04,14.46,18.87,21.31,42.26,42.32,106.11,73.35,201.59,73.44,145.66.13,270.46-78.6,346.37-268.97,24.98.41,90.92,4.48,123.19-57.88.79-1.05,8.21-16.54,8.21-16.54l-12.3-8.27ZM189.67,206.39h-81.7v81.7h81.7v-81.7ZM295.22,206.39h-81.7v81.7h81.7v-81.7ZM400.77,206.39h-81.7v81.7h81.7v-81.7ZM506.32,206.39h-81.7v81.7h81.7v-81.7ZM84.12,206.39H2.42v81.7h81.7v-81.7ZM189.67,103.2h-81.7v81.7h81.7v-81.7ZM295.22,103.2h-81.7v81.7h81.7v-81.7ZM400.77,103.2h-81.7v81.7h81.7v-81.7ZM400.77,0h-81.7v81.7h81.7V0Z"/></svg>`,

    // Kubernetes logo (simplified)
    k8s: `<svg viewBox="0 -3.5 256 256" width="40" height="40"><path fill="#326DE6" d="M82.0851613,244.934194 C76.1393548,244.934194 70.523871,242.291613 66.7251613,237.501935 L8.91870968,165.656774 C5.12,160.867097 3.63354839,154.756129 5.12,148.810323 L25.7651613,59.1277419 C27.0864516,53.1819355 31.0503226,48.3922581 36.5006452,45.7496774 L120.072258,5.78064516 C122.714839,4.45935484 125.687742,3.79870968 128.660645,3.79870968 C131.633548,3.79870968 134.606452,4.45935484 137.249032,5.78064516 L220.820645,45.5845161 C226.270968,48.2270968 230.234839,53.0167742 231.556129,58.9625806 L252.20129,148.645161 C253.522581,154.590968 252.20129,160.701935 248.402581,165.491613 L190.596129,237.336774 C186.797419,241.96129 181.181935,244.769032 175.236129,244.769032 L82.0851613,244.934194 L82.0851613,244.934194 Z"/><path fill="#FFFFFF" d="M128.495484,7.92774194 C130.807742,7.92774194 133.12,8.42322581 135.267097,9.41419355 L218.83871,49.2180645 C223.132903,51.3651613 226.436129,55.3290323 227.427097,59.9535484 L248.072258,149.636129 C249.228387,154.425806 248.072258,159.380645 244.934194,163.179355 L187.127742,235.024516 C184.154839,238.823226 179.530323,240.970323 174.740645,240.970323 L82.0851613,240.970323 C77.2954839,240.970323 72.6709677,238.823226 69.6980645,235.024516 L11.8916129,163.179355 C8.91870968,159.380645 7.76258065,154.425806 8.75354839,149.636129 L29.3987097,59.9535484 C30.5548387,55.163871 33.6929032,51.2 37.9870968,49.2180645 L121.55871,9.24903226 C123.705806,8.42322581 126.183226,7.92774194 128.495484,7.92774194 L128.495484,7.92774194 Z M128.495484,0.16516129 L128.495484,0.16516129 C125.027097,0.16516129 121.55871,0.990967742 118.255484,2.47741935 L34.683871,42.4464516 C28.0774194,45.5845161 23.4529032,51.3651613 21.8012903,58.4670968 L1.15612903,148.149677 C-0.495483871,155.251613 1.15612903,162.51871 5.78064516,168.299355 L63.5870968,240.144516 C68.0464516,245.76 74.8180645,248.898065 81.92,248.898065 L174.575484,248.898065 C181.677419,248.898065 188.449032,245.76 192.908387,240.144516 L250.714839,168.299355 C255.339355,162.683871 256.990968,155.251613 255.339355,148.149677 L234.694194,58.4670968 C233.042581,51.3651613 228.418065,45.5845161 221.811613,42.4464516 L138.570323,2.47741935 C135.432258,0.990967742 131.963871,0.16516129 128.495484,0.16516129 L128.495484,0.16516129 L128.495484,0.16516129 Z"/><path fill="#FFFFFF" d="M212.232258,142.534194 C212.067097,142.534194 212.067097,142.534194 212.232258,142.534194 L212.067097,142.534194 C211.901935,142.534194 211.736774,142.534194 211.736774,142.369032 C211.406452,142.369032 211.076129,142.203871 210.745806,142.203871 C209.589677,142.03871 208.59871,141.873548 207.607742,141.873548 C207.112258,141.873548 206.616774,141.873548 205.956129,141.708387 L205.790968,141.708387 C202.322581,141.378065 199.514839,141.047742 196.872258,140.221935 C195.716129,139.726452 195.385806,139.065806 195.055484,138.405161 C195.055484,138.24 194.890323,138.24 194.890323,138.074839 L192.743226,137.414194 C193.734194,129.816774 193.403871,121.889032 191.587097,114.126452 C189.770323,106.363871 186.632258,99.0967742 182.338065,92.4903226 L183.989677,91.003871 L183.989677,90.6735484 C183.989677,89.8477419 184.154839,89.0219355 184.815484,88.196129 C186.797419,86.3793548 189.274839,84.8929032 192.247742,83.076129 C192.743226,82.7458065 193.23871,82.5806452 193.734194,82.2503226 C194.725161,81.7548387 195.550968,81.2593548 196.541935,80.5987097 C196.707097,80.4335484 197.037419,80.2683871 197.367742,79.9380645 C197.532903,79.7729032 197.698065,79.7729032 197.698065,79.6077419 C200.010323,77.6258065 200.505806,74.3225806 198.854194,72.1754839 C198.028387,71.0193548 196.541935,70.3587097 195.055484,70.3587097 C193.734194,70.3587097 192.578065,70.8541935 191.421935,71.68 C191.256774,71.8451613 191.256774,71.8451613 191.091613,72.0103226 C190.76129,72.1754839 190.596129,72.5058065 190.265806,72.6709677 C189.44,73.4967742 188.779355,74.1574194 188.11871,74.9832258 C187.788387,75.3135484 187.458065,75.8090323 186.962581,76.1393548 C184.650323,78.6167742 182.503226,80.5987097 180.356129,82.0851613 C179.860645,82.4154839 179.365161,82.5806452 178.869677,82.5806452 C178.539355,82.5806452 178.209032,82.5806452 177.87871,82.4154839 L177.548387,82.4154839 L175.566452,83.7367742 C173.419355,81.4245161 171.107097,79.4425806 168.794839,77.4606452 C158.885161,69.6980645 146.828387,64.9083871 134.276129,63.7522581 L134.110968,61.6051613 C133.945806,61.44 133.945806,61.44 133.780645,61.2748387 C133.285161,60.7793548 132.624516,60.283871 132.459355,59.1277419 C132.294194,56.4851613 132.624516,53.5122581 132.954839,50.2090323 L132.954839,50.043871 C132.954839,49.5483871 133.12,48.8877419 133.285161,48.3922581 C133.450323,47.4012903 133.615484,46.4103226 133.780645,45.2541935 L133.780645,44.2632258 L133.780645,43.7677419 C133.780645,40.7948387 131.468387,38.3174194 128.660645,38.3174194 C127.339355,38.3174194 126.018065,38.9780645 125.027097,39.9690323 C124.036129,40.96 123.540645,42.2812903 123.540645,43.7677419 L123.540645,44.0980645 L123.540645,45.0890323 C123.540645,46.2451613 123.705806,47.236129 124.036129,48.2270968 C124.20129,48.7225806 124.20129,49.2180645 124.366452,49.8787097 L124.366452,50.043871 C124.696774,53.3470968 125.192258,56.32 124.861935,58.9625806 C124.696774,60.1187097 124.036129,60.6141935 123.540645,61.1096774 C123.375484,61.2748387 123.375484,61.2748387 123.210323,61.44 L123.045161,63.5870968 C120.072258,63.9174194 117.099355,64.2477419 114.126452,64.9083871 C101.409032,67.716129 90.1780645,74.1574194 81.4245161,83.4064516 L79.7729032,82.2503226 L79.4425806,82.2503226 C79.1122581,82.2503226 78.7819355,82.4154839 78.4516129,82.4154839 C77.956129,82.4154839 77.4606452,82.2503226 76.9651613,81.92 C74.8180645,80.4335484 72.6709677,78.2864516 70.3587097,75.8090323 C70.0283871,75.4787097 69.6980645,74.9832258 69.2025806,74.6529032 C68.5419355,73.8270968 67.8812903,73.1664516 67.0554839,72.3406452 C66.8903226,72.1754839 66.56,72.0103226 66.2296774,71.68 C66.0645161,71.5148387 65.8993548,71.5148387 65.8993548,71.3496774 C64.9083871,70.523871 63.5870968,70.0283871 62.2658065,70.0283871 C60.7793548,70.0283871 59.2929032,70.6890323 58.4670968,71.8451613 C56.8154839,73.9922581 57.3109677,77.2954839 59.6232258,79.2774194 C59.7883871,79.2774194 59.7883871,79.4425806 59.9535484,79.4425806 C60.283871,79.6077419 60.4490323,79.9380645 60.7793548,80.1032258 C61.7703226,80.763871 62.596129,81.2593548 63.5870968,81.7548387 C64.0825806,81.92 64.5780645,82.2503226 65.0735484,82.5806452 C68.0464516,84.3974194 70.523871,85.883871 72.5058065,87.7006452 C73.3316129,88.5264516 73.3316129,89.3522581 73.3316129,90.1780645 L73.3316129,90.5083871 L74.9832258,91.9948387 C74.6529032,92.4903226 74.3225806,92.8206452 74.1574194,93.316129 C65.8993548,106.363871 62.7612903,121.723871 64.9083871,136.91871 L62.7612903,137.579355 C62.7612903,137.744516 62.596129,137.744516 62.596129,137.909677 C62.2658065,138.570323 61.7703226,139.230968 60.7793548,139.726452 C58.3019355,140.552258 55.3290323,140.882581 51.8606452,141.212903 L51.6954839,141.212903 C51.2,141.212903 50.5393548,141.212903 50.043871,141.378065 C49.0529032,141.378065 48.0619355,141.543226 46.9058065,141.708387 C46.5754839,141.708387 46.2451613,141.873548 45.9148387,141.873548 C45.7496774,141.873548 45.5845161,141.873548 45.4193548,142.03871 C42.4464516,142.699355 40.6296774,145.507097 41.1251613,148.149677 C41.6206452,150.461935 43.7677419,151.948387 46.4103226,151.948387 C46.9058065,151.948387 47.236129,151.948387 47.7316129,151.783226 C47.8967742,151.783226 48.0619355,151.783226 48.0619355,151.618065 C48.3922581,151.618065 48.7225806,151.452903 49.0529032,151.452903 C50.2090323,151.122581 51.0348387,150.792258 52.0258065,150.296774 C52.5212903,150.131613 53.0167742,149.80129 53.5122581,149.636129 L53.6774194,149.636129 C56.8154839,148.48 59.6232258,147.489032 62.2658065,147.15871 L62.596129,147.15871 C63.5870968,147.15871 64.2477419,147.654194 64.7432258,147.984516 C64.9083871,147.984516 64.9083871,148.149677 65.0735484,148.149677 L67.3858065,147.819355 C71.3496774,160.04129 78.9470968,170.941935 89.0219355,178.869677 C91.3341935,180.686452 93.6464516,182.172903 96.123871,183.659355 L95.1329032,185.806452 C95.1329032,185.971613 95.2980645,185.971613 95.2980645,186.136774 C95.6283871,186.797419 95.9587097,187.623226 95.6283871,188.779355 C94.6374194,191.256774 93.1509677,193.734194 91.3341935,196.541935 L91.3341935,196.707097 C91.003871,197.202581 90.6735484,197.532903 90.3432258,198.028387 C89.6825806,198.854194 89.1870968,199.68 88.5264516,200.670968 C88.3612903,200.836129 88.196129,201.166452 88.0309677,201.496774 C88.0309677,201.661935 87.8658065,201.827097 87.8658065,201.827097 C86.5445161,204.634839 87.5354839,207.772903 90.0129032,208.929032 C90.6735484,209.259355 91.3341935,209.424516 91.9948387,209.424516 C93.9767742,209.424516 95.9587097,208.103226 96.9496774,206.286452 C96.9496774,206.12129 97.1148387,205.956129 97.1148387,205.956129 C97.28,205.625806 97.4451613,205.295484 97.6103226,205.130323 C98.1058065,203.974194 98.2709677,203.148387 98.6012903,202.157419 C98.7664516,201.661935 98.9316129,201.166452 99.0967742,200.670968 C100.252903,197.367742 101.07871,194.725161 102.565161,192.412903 C103.225806,191.421935 104.051613,191.256774 104.712258,190.926452 C104.877419,190.926452 104.877419,190.926452 105.042581,190.76129 L106.19871,188.614194 C113.465806,191.421935 121.393548,192.908387 129.32129,192.908387 C134.110968,192.908387 139.065806,192.412903 143.690323,191.256774 C146.663226,190.596129 149.470968,189.770323 152.27871,188.779355 L153.269677,190.596129 C153.434839,190.596129 153.434839,190.596129 153.6,190.76129 C154.425806,190.926452 155.086452,191.256774 155.747097,192.247742 C157.068387,194.56 158.059355,197.367742 159.215484,200.505806 L159.215484,200.670968 C159.380645,201.166452 159.545806,201.661935 159.710968,202.157419 C160.04129,203.148387 160.206452,204.139355 160.701935,205.130323 C160.867097,205.460645 161.032258,205.625806 161.197419,205.956129 C161.197419,206.12129 161.362581,206.286452 161.362581,206.286452 C162.353548,208.268387 164.335484,209.424516 166.317419,209.424516 C166.978065,209.424516 167.63871,209.259355 168.299355,208.929032 C169.455484,208.268387 170.446452,207.277419 170.776774,205.956129 C171.107097,204.634839 171.107097,203.148387 170.446452,201.827097 C170.446452,201.661935 170.28129,201.661935 170.28129,201.496774 C170.116129,201.166452 169.950968,200.836129 169.785806,200.670968 C169.290323,199.68 168.629677,198.854194 167.969032,198.028387 C167.63871,197.532903 167.308387,197.202581 166.978065,196.707097 L166.978065,196.541935 C165.16129,193.734194 163.509677,191.256774 162.683871,188.779355 C162.353548,187.623226 162.683871,186.962581 162.849032,186.136774 C162.849032,185.971613 163.014194,185.971613 163.014194,185.806452 L162.188387,183.824516 C170.941935,178.704516 178.374194,171.437419 183.989677,162.51871 C186.962581,157.894194 189.274839,152.774194 190.926452,147.654194 L192.908387,147.984516 C193.073548,147.984516 193.073548,147.819355 193.23871,147.819355 C193.899355,147.489032 194.394839,146.993548 195.385806,146.993548 L195.716129,146.993548 C198.35871,147.323871 201.166452,148.314839 204.304516,149.470968 L204.469677,149.470968 C204.965161,149.636129 205.460645,149.966452 205.956129,150.131613 C206.947097,150.627097 207.772903,150.957419 208.929032,151.287742 C209.259355,151.287742 209.589677,151.452903 209.92,151.452903 C210.085161,151.452903 210.250323,151.452903 210.415484,151.618065 C210.910968,151.783226 211.24129,151.783226 211.736774,151.783226 C214.214194,151.783226 216.36129,150.131613 217.021935,147.984516 C217.021935,146.002581 215.205161,143.36 212.232258,142.534194 Z M135.762581,134.44129 L128.495484,137.909677 L121.228387,134.44129 L119.411613,126.67871 L124.366452,120.402581 L132.459355,120.402581 L137.414194,126.67871 L135.762581,134.44129 Z M178.869677,117.264516 C180.190968,122.88 180.52129,128.495484 180.025806,133.945806 L154.756129,126.67871 C152.443871,126.018065 151.122581,123.705806 151.618065,121.393548 C151.783226,120.732903 152.113548,120.072258 152.609032,119.576774 L172.593548,101.574194 C175.40129,106.19871 177.548387,111.483871 178.869677,117.264516 Z M164.665806,91.6645161 L143.029677,107.024516 C141.212903,108.180645 138.735484,107.850323 137.249032,106.033548 C136.753548,105.538065 136.588387,104.877419 136.423226,104.216774 L134.936774,77.2954839 C146.332903,78.6167742 156.738065,83.7367742 164.665806,91.6645161 Z M116.769032,78.1212903 C118.585806,77.7909677 120.237419,77.4606452 122.054194,77.1303226 L120.567742,103.556129 C120.402581,105.868387 118.585806,107.850323 116.108387,107.850323 C115.447742,107.850323 114.621935,107.685161 114.126452,107.354839 L92.16,91.6645161 C98.9316129,84.8929032 107.354839,80.2683871 116.769032,78.1212903 Z M84.2322581,101.574194 L103.886452,119.08129 C105.703226,120.567742 105.868387,123.375484 104.381935,125.192258 C103.886452,125.852903 103.225806,126.348387 102.4,126.513548 L76.8,133.945806 C75.8090323,122.714839 78.2864516,111.31871 84.2322581,101.574194 Z M79.7729032,146.332903 L106.033548,141.873548 C108.180645,141.708387 110.162581,143.194839 110.658065,145.341935 C110.823226,146.332903 110.823226,147.15871 110.492903,147.984516 L100.418065,172.263226 C91.1690323,166.317419 83.7367742,157.233548 79.7729032,146.332903 Z M140.056774,179.2 C136.258065,180.025806 132.459355,180.52129 128.495484,180.52129 C122.714839,180.52129 117.099355,179.530323 111.814194,177.87871 L124.861935,154.260645 C126.183226,152.774194 128.330323,152.113548 130.147097,153.104516 C130.972903,153.6 131.633548,154.260645 132.129032,154.92129 L144.846452,177.87871 C143.36,178.374194 141.708387,178.704516 140.056774,179.2 Z M172.263226,156.242581 C168.134194,162.849032 162.683871,168.134194 156.407742,172.263226 L146.002581,147.323871 C145.507097,145.341935 146.332903,143.194839 148.314839,142.203871 C148.975484,141.873548 149.80129,141.708387 150.627097,141.708387 L177.052903,146.167742 C176.061935,149.80129 174.410323,153.104516 172.263226,156.242581 Z"/></svg>`,

    // ── XMPP strategy cards (Step 1 — Docker/K8s) ──────────────
    // (replaced by real image files; kept as fallback SVGs in JS only)

    ejabberd: `<svg viewBox="0 0 64 64" width="42" height="42" xmlns="http://www.w3.org/2000/svg">
        <rect x="4" y="4" width="56" height="56" rx="12" ry="12" fill="#e05206"/>
        <text x="32" y="46" font-size="30" font-weight="bold" text-anchor="middle" fill="#ffffff"
              font-family="Arial, Helvetica, sans-serif">ej</text>
    </svg>`,

    xmpp: `<svg viewBox="0 0 64 64" width="42" height="42" xmlns="http://www.w3.org/2000/svg">
        <rect x="4" y="4" width="56" height="56" rx="12" ry="12" fill="#009900"/>
        <text x="32" y="47" font-size="38" font-weight="bold" text-anchor="middle" fill="#ffffff"
              font-family="Arial, Helvetica, sans-serif">X</text>
    </svg>`,

    // ── AAS server strategy cards (Step 2) ──────────────────────

    basyx: `<svg viewBox="0 0 64 64" width="42" height="42" xmlns="http://www.w3.org/2000/svg">
        <rect x="4" y="4" width="56" height="56" rx="10" ry="10" fill="#003366"/>
        <text x="32" y="24" font-size="10" font-weight="bold" text-anchor="middle" fill="#ffffff"
              font-family="Arial, Helvetica, sans-serif">BaSyx</text>
        <rect x="12" y="30" width="40" height="7" rx="2" fill="#4da6ff"/>
        <rect x="12" y="41" width="28" height="7" rx="2" fill="#4da6ff" opacity="0.55"/>
    </svg>`,

    // Uses currentColor so the SVG respects the parent element's CSS color
    serverExternal: `<svg viewBox="0 0 24 24" width="36" height="36" fill="none" xmlns="http://www.w3.org/2000/svg">
        <rect x="2" y="3"  width="20" height="5" rx="1.5" fill="var(--color-brand-primary)" opacity="0.2" stroke="var(--color-brand-primary)" stroke-width="1.2"/>
        <rect x="2" y="10" width="20" height="5" rx="1.5" fill="var(--color-brand-primary)" opacity="0.2" stroke="var(--color-brand-primary)" stroke-width="1.2"/>
        <rect x="2" y="17" width="20" height="5" rx="1.5" fill="var(--color-brand-primary)" opacity="0.2" stroke="var(--color-brand-primary)" stroke-width="1.2"/>
        <circle cx="5.5" cy="5.5"  r="1" fill="var(--color-brand-primary)"/>
        <circle cx="5.5" cy="12.5" r="1" fill="var(--color-brand-primary)"/>
        <circle cx="5.5" cy="19.5" r="1" fill="var(--color-brand-primary)"/>
    </svg>`,

    fileMode: `<svg viewBox="0 0 24 24" width="36" height="36" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M14 2H6c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V8l-6-6z"
              fill="var(--color-foreground-secondary)" opacity="0.15"/>
        <path d="M14 2H6c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V8l-6-6z"
              stroke="var(--color-foreground-secondary)" stroke-width="1.4" fill="none"/>
        <path d="M14 2v6h6" stroke="var(--color-foreground-secondary)" stroke-width="1.4" fill="none"/>
        <line x1="8" y1="13" x2="16" y2="13" stroke="var(--color-foreground-secondary)" stroke-width="1.2" stroke-linecap="round"/>
        <line x1="8" y1="16" x2="13" y2="16" stroke="var(--color-foreground-secondary)" stroke-width="1.2" stroke-linecap="round"/>
    </svg>`,

    // ── ZIP / AASX file upload icon ──────────────────────────────
    zipFile: `<svg viewBox="0 0 24 24" width="24" height="24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M13 2H6C4.895 2 4 2.895 4 4v16c0 1.105.895 2 2 2h12c1.105 0 2-.895 2-2V9l-7-7z"
              fill="currentColor" opacity="0.12"/>
        <path d="M13 2H6C4.895 2 4 2.895 4 4v16c0 1.105.895 2 2 2h12c1.105 0 2-.895 2-2V9l-7-7z"
              stroke="currentColor" stroke-width="1.5" fill="none" stroke-linejoin="round"/>
        <path d="M13 2v7h7" stroke="currentColor" stroke-width="1.5" fill="none" stroke-linejoin="round"/>
        <line x1="12" y1="9"  x2="12" y2="20" stroke="currentColor" stroke-width="1" stroke-dasharray="1.5 1.5" stroke-linecap="round"/>
        <rect x="9.5"  y="10.5" width="2" height="1.5" rx="0.4" fill="currentColor"/>
        <rect x="9.5"  y="13.5" width="2" height="1.5" rx="0.4" fill="currentColor"/>
        <rect x="9.5"  y="16.5" width="2" height="1.5" rx="0.4" fill="currentColor"/>
        <rect x="12.5" y="11.5" width="2" height="1.5" rx="0.4" fill="currentColor"/>
        <rect x="12.5" y="14.5" width="2" height="1.5" rx="0.4" fill="currentColor"/>
        <rect x="12.5" y="17.5" width="2" height="1.5" rx="0.4" fill="currentColor"/>
        <rect x="10.5" y="8" width="3" height="2" rx="0.5" fill="currentColor"/>
    </svg>`,

    // ── Summary section title icons (inline, small) ─────────────
    // Uses var(--color-brand-primary) so they adapt to theme colour

    summaryInfra: `<svg viewBox="0 0 16 16" width="14" height="14" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
        <path d="M2 2h12v3H2zm0 4h12v3H2zm0 4h12v3H2z" opacity="0.5"/>
        <circle cx="3.5" cy="3.5"  r="1" fill="var(--color-brand-primary)"/>
        <circle cx="3.5" cy="7.5"  r="1" fill="var(--color-brand-primary)"/>
        <circle cx="3.5" cy="11.5" r="1" fill="var(--color-brand-primary)"/>
    </svg>`,

    summaryServices: `<svg viewBox="0 0 16 16" width="14" height="14" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
        <path d="M8 2a6 6 0 100 12A6 6 0 008 2zm0 1.5a4.5 4.5 0 110 9 4.5 4.5 0 010-9zm0 1.5a3 3 0 100 6 3 3 0 000-6z" opacity="0.5"/>
        <circle cx="8" cy="8" r="1.5" fill="var(--color-brand-primary)"/>
    </svg>`,

    summaryAssets: `<svg viewBox="0 0 16 16" width="14" height="14" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
        <rect x="1" y="4" width="6" height="8" rx="1" opacity="0.5"/>
        <rect x="9" y="4" width="6" height="8" rx="1" opacity="0.5"/>
        <line x1="7" y1="8" x2="9" y2="8" stroke="var(--color-brand-primary)" stroke-width="1.5" stroke-linecap="round"/>
    </svg>`,
};

const GITHUB_URLS = {
    // Raw Python launcher for Standard SMIA instance
    LAUNCHER: 'https://raw.githubusercontent.com/ekhurtado/SMIA/refs/heads/main/examples/smia_extended/extended_smia_launcher.py',   // TODO AÑADIR EL LAUNCHER NORMAL DE SMIA EN GITHUB
    // Raw Python launcher for Extended SMIA instance
    EXTENDED_LAUNCHER: 'https://raw.githubusercontent.com/ekhurtado/SMIA/refs/heads/main/examples/smia_extended/extended_smia_launcher.py',
    // Dockerfile for Extended SMIA Docker build
    DOCKERFILE: 'https://raw.githubusercontent.com/ekhurtado/SMIA/refs/heads/main/examples/smia_extended/Dockerfile',
    // GitHub archive URL for SMIA Operator agent repository
    GITHUB_TREE: `https://api.github.com/repos/ekhurtado/SMIA/git/trees/main?recursive=1`,
    OPERATOR_SUBFOLDER: 'additional_tools/extended_agents/smia_operator_agent',
    OPERATOR_RAW_BASE: `https://raw.githubusercontent.com/ekhurtado/SMIA/main/`,
    // SMIA ISM AAS model file
    ISM_AASX: 'https://raw.githubusercontent.com/ekhurtado/SMIA/refs/heads/main/additional_tools/infrastructure_components/smia_ism/deploy/aas/SMIA_InfrastructureServicesManager.aasx',
    // SMIA Operator docker-compose and AAS model file
    OPERATOR_DOCKER_COMPOSE: 'https://raw.githubusercontent.com/ekhurtado/SMIA/refs/heads/main/additional_tools/extended_agents/smia_operator_agent/deploy/docker-compose.yml',
    //OPERATOR_AASX: 'https://raw.githubusercontent.com/ekhurtado/SMIA/refs/heads/main/additional_tools/extended_agents/smia_operator_agent/SMIA_operator.aasx',
    OPERATOR_AASX: 'https://raw.githubusercontent.com/ekhurtado/SMIA/refs/heads/main/use_cases/simple_human_in_the_mesh/deploy/aas/SMIA_Operator_article.aasx',
    CSS_ONTOLOGY: 'https://raw.githubusercontent.com/ekhurtado/SMIA/refs/heads/main/additional_resources/css_smia_ontology/CSS-ontology-smia.owl',
    // Assets Simulator HTTP project subfolder in the SMIA repository
    ASSETS_SIMULATOR_SUBFOLDER: 'additional_tools/assets_simulators/assets_simulator_http',
};

/* ============================================================
   MAIN MODULE
   ============================================================ */
const SMIA_Builder = {
    state: {
        step: 0,
        envType: null, // 'local' | 'docker' | 'k8s'

        localSettings: {
            instanceType: 'normal' // 'normal' | 'extended' | 'both'
        },

        xmpp: {
            strategy: 'new', // 'new' | 'existing'
            domain: '',
            ip: ''
        },

        core: {
            smiakb: false,
            ism: false,
            aasServer: { type: 'basyx', ip: '127.0.0.1', basyxVariant: 'go' }
        },

        plan: { hasPlan: false, file: null, path: '' },
        assets: [], // [{ path, file, isExtended, image }]
        operator: false,
        assetsSimulator: {
            enabled: false,
            productionAssets: '',
            mobileAssets: '',
            humanAssets: ''
        }
    },

    init: function () {
        this.renderInitialState();
        this.bindEvents();
    },

    // ============================================================
    // RENDER
    // ============================================================

    renderInitialState: function () {
        const root = document.getElementById("smia-builder-root");
        root.innerHTML = `
            <div class="smia-wizard-container">
                <div class="smia-progress-bar" id="progress-bar-container" style="display:none;">
                    <div class="progress-fill" id="progress-fill" style="width: 0%"></div>
                </div>

                <!-- ── STEP 0: Welcome ── -->
                <div class="smia-welcome-screen active" id="step-0">
                    <img src="_static/images/environment_builder_images/SMIA_environment_builder_icon.svg" class="welcome-icon" alt="SMIA Icon">
                    <h2 class="welcome-title">SMIA Environment Builder</h2>
                    <p class="welcome-text">
                        Set up your SMIA workspace automatically with this tool. Simply select your target ecosystem (Local, 
                        Docker Compose, or Kubernetes) and configure your infrastructure services and SMIA instances 
                        to get a ready-to-use environment.
                    </p>
                    <button id="btn-start" class="smia-btn primary btn-large">Start Configuration</button>
                </div>

                <!-- ── STEP 1: Base Infrastructure ── -->
                <div class="smia-step" id="step-1">
                    <h3>Step 1: Base Environment</h3>

                    <label class="section-label">Select your working environment:</label>
                    <div class="env-grid">
                        <div class="env-card" data-env="local">
                            <span class="card-icon">${ICONS.local}</span>
                            <span class="card-title">Local (Python)</span>
                            <span class="card-desc">Container-less environment for development and local Python execution.</span>
                        </div>
                        <div class="env-card" data-env="docker">
                            <span class="card-icon">${ICONS.docker}</span>
                            <span class="card-title">Docker Compose</span>
                            <span class="card-desc">Standard containerized environment, ideal for testing and single-node deployments.</span>
                        </div>
                        <div class="env-card" data-env="k8s">
                            <span class="card-icon">${ICONS.k8s}</span>
                            <span class="card-title">Kubernetes</span>
                            <span class="card-desc">Scalable distributed environment, ideal for workload distribution and multi-node deployments.</span>
                        </div>
                    </div>
                    <div id="env-error" style="color: var(--color-problematic); display:none; margin-bottom:1rem;">
                        ⚠️ Please select an environment.
                    </div>

                    <div id="dynamic-infra-options" style="display:none; margin-top: 2rem; border-top: 1px solid var(--color-border); padding-top: 1.5rem;">

                        <!-- LOCAL -->
                        <div id="local-options-group" style="display:none;">
                            <label class="section-label">Local Configuration:</label>
                            <div class="form-group" style="margin-bottom: 1.5rem;">
                                <label for="xmpp-domain-local">XMPP Domain (Required for scripts)</label>
                                <input type="text" id="xmpp-domain-local" placeholder="e.g., localhost" class="smia-input">
                            </div>
                            <label class="section-label">Python Scaffolding Type:</label>
                            <div class="env-grid" style="grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); margin-bottom: 0;">
                                <div class="option-card selected" data-local-type="normal">
                                    <img src="_static/images/environment_builder_images/SMIA_DT_icon.svg" alt="Standard" class="card-local-img"
                                         onerror="this.style.display='none'">
                                    <strong>Standard</strong>
                                </div>
                                <div class="option-card" data-local-type="extended">
                                    <img src="_static/images/environment_builder_images/SMIA_DT_extended_icon.svg" alt="Extended" class="card-local-img"
                                         onerror="this.style.display='none'">
                                    <strong>Extended</strong>
                                </div>
                                <div class="option-card" data-local-type="both">
                                    <img src="_static/images/environment_builder_images/SMIA_DT_both_standard_extended_icon.svg" alt="Both" class="card-local-img"
                                         onerror="this.style.display='none'">
                                    <strong>Both</strong>
                                </div>
                            </div>
                        </div>

                        <!-- DOCKER/K8S XMPP -->
                        <div id="container-xmpp-options" style="display:none;">
                            <label class="section-label">XMPP Server Configuration:</label>
                            <div class="env-grid" style="grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); margin-bottom: 1rem;">
                                <div class="option-card selected" data-xmpp-strat="new">
                                    <img src="_static/images/environment_builder_images/Ejabberd_icon.png" alt="Ejabberd" class="card-local-img"
                                         onerror="this.style.display='none'">
                                    <strong>Deploy New</strong>
                                    <small style="display:block; color:var(--color-foreground-secondary)">Ejabberd Container</small>
                                </div>
                                <div class="option-card" data-xmpp-strat="existing">
                                    <img src="_static/images/environment_builder_images/XMPP_logo.png" alt="XMPP" class="card-local-img"
                                         onerror="this.style.display='none'">
                                    <strong>Use Existing</strong>
                                    <small style="display:block; color:var(--color-foreground-secondary)">External XMPP Server</small>
                                </div>
                            </div>
                            <div id="xmpp-details-section" style="display:none; margin-top: 1.5rem; background: var(--color-background-secondary); padding: 1.5rem; border-radius: 6px; border: 1px solid var(--color-border);">
                                <label class="section-label" style="margin-bottom: 0.5rem;">Connection Details</label>
                                <div class="form-group">
                                    <label for="xmpp-domain">Domain Name</label>
                                    <input type="text" id="xmpp-domain" placeholder="e.g., smia.net" class="smia-input">
                                </div>
                                <div class="form-group">
                                    <label for="xmpp-ip">Server IP Address</label>
                                    <input type="text" id="xmpp-ip" placeholder="e.g., 192.168.1.50" class="smia-input">
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- ── STEP 2: Core SMIA Services ── -->
                <div class="smia-step" id="step-2">
                    <h3>Step 2: Infrastructure Services</h3>

                    <label class="section-label">SMIA infrastructure</label>
                    <div class="env-grid" style="grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); margin-bottom: 1rem;">

                        <div class="toggle-card" id="card-kb">
                            <span class="toggle-card-badge"></span>
                            <input type="checkbox" id="chk-kb">
                            <img src="_static/images/environment_builder_images/SMIA_I_KB_icon.svg" alt="SMIA-I KB" class="card-service-img"
                                 onerror="this.style.display='none'; this.nextElementSibling.style.display='block'">
                            <span class="toggle-icon" style="display:none;">🧠</span>
                            <strong>SMIA-I KB</strong>
                        </div>

                        <div class="toggle-card" id="card-ism">
                            <span class="toggle-card-badge"></span>
                            <input type="checkbox" id="chk-ism">
                            <img src="_static/images/environment_builder_images/SMIA_ISM_icon.svg" alt="SMIA ISM" class="card-service-img"
                                 onerror="this.style.display='none'; this.nextElementSibling.style.display='block'">
                            <span class="toggle-icon" style="display:none;">🌐</span>
                            <strong>SMIA ISM</strong>
                        </div>
                    </div>

                    <div class="info-box" id="ism-dependency-notice" style="display:none; margin-bottom: 1.5rem;">
                        ℹ️ <strong>Dependency:</strong> SMIA ISM is required by SMIA-I KB and has been enabled automatically.
                    </div>
                    <div class="info-box" id="ism-warning-notice" style="display:none; margin-bottom: 1.5rem; background-color: rgba(255, 193, 7, 0.1); border-left-color: #ffc107;">
                        ⚠️ <strong>Warning:</strong> SMIA ISM cannot be disabled while SMIA-I KB is enabled. Please disable SMIA-I KB first.
                    </div>

                    <label class="section-label">AAS Server</label>
                    <div class="env-grid" style="grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 1rem;">
                        <div class="option-card selected" data-aas="basyx">
                            <img src="_static/images/environment_builder_images/basyxlogo.png" alt="BaSyx" class="card-local-img"
                                 onerror="this.style.display='none'">
                            <strong>Deploy Basyx</strong>
                        </div>
                        <div class="option-card" data-aas="external">
                            <img src="_static/images/environment_builder_images/AAS_server_icon.svg" alt="AAS Server" class="card-local-img"
                                 onerror="this.style.display='none'">
                            <strong>Use Existing</strong>
                        </div>
                        <div class="option-card" data-aas="none">
                            <span class="card-icon-svg">${ICONS.fileMode}</span>
                            <strong>None</strong>
                            <small style="color:var(--color-foreground-secondary); font-size:0.8rem;">(File Mode)</small>
                        </div>
                    </div>
                    <div id="aas-external-inputs" style="display:none; margin-top:1.5rem; padding: 1rem; background: var(--color-background-secondary); border-radius: 6px; border: 1px solid var(--color-border);">
                        <label>AAS Server IP</label>
                        <input type="text" id="aas-ip" class="smia-input" placeholder="e.g., 10.0.0.5">
                    </div>
                    <div id="basyx-variant-selector" style="margin-top:1rem; padding: 0.7rem 1rem; background: var(--color-background-secondary); border-radius: 6px; border: 1px solid var(--color-border); display: flex; align-items: center; gap: 0.75rem; flex-wrap: wrap;">
                        <span style="color: var(--color-foreground-secondary);">BaSyx version:</span>
                        <div class="segmented-selector">
                            <div class="segmented-option selected" data-basyx-variant="go">Go</div>
                            <div class="segmented-option" data-basyx-variant="java">Java</div>
                        </div>
                    </div>
                </div>

                <!-- ── STEP 3: Assets & Manufacturing ── -->
                <div class="smia-step" id="step-3">
                    <h3 id="step-3-title">Step 3: Manufacturing assets</h3>

                    <div id="step-3-intro-local" style="display:none; margin-bottom:1.5rem; color:var(--color-foreground-secondary)">
                        Add a single Asset file to be included in your local environment ZIP.
                    </div>

                    <!-- Manufacturing Plan (hidden in local mode) -->
                    <div class="asset-card" id="plan-card-container">
                        <h4>Manufacturing Plan asset (optional)</h4>
                        <label class="modern-checkbox">
                            <input type="checkbox" id="chk-has-plan">
                            <span class="checkmark"></span>
                            Include CSS-enriched Manufacturing Plan
                        </label>
                        <div id="plan-inputs" style="display:none; margin-top: 10px;">
                            <div class="file-upload-wrapper">
                                <input type="file" id="plan-file" class="file-upload-input" accept=".aasx"
                                       onchange="SMIA_Builder.handleFileSelect(this)">
                                <div class="file-upload-label">
                                    <span class="file-text">Click to upload AASX file...</span>
                                    <span class="upload-icon">${ICONS.zipFile}</span>
                                </div>
                            </div>
                            <small style="display:block; margin: 8px 0; color: var(--color-foreground-secondary);">Or manually specify path/ID:</small>
                            <input type="text" id="plan-path" placeholder="/app/models/plan.aasx or AAS-ID" class="smia-input">
                            
                            <div class="form-group" style="display: flex; gap: 1rem; margin-top: 15px;">
                                <div style="flex: 1;">
                                    <label>Agent JID</label>
                                    <input type="text" id="plan-jid" class="smia-input" placeholder="e.g., smia-1">
                                </div>
                                <div style="flex: 1;">
                                    <label>Agent Password</label>
                                    <input type="text" id="plan-password" class="smia-input" placeholder="e.g., 1234">
                                </div>
                            </div>
                        </div>
                    </div>

                    <label class="section-label" style="margin-top: 2rem;">Production Assets</label>
                    <div id="assets-list"></div>
                    <button class="smia-btn secondary" id="btn-add-asset" style="width:100%">+ Add asset instance</button>

                    <!-- Operator section — always visible (local AND docker/k8s) -->
                    <div id="operator-section" style="margin-top: 2rem; border-top: 1px solid var(--color-border); padding-top: 2rem;">
                        <label class="section-label">Operator Dashboard</label>
                        <div class="env-grid" style="grid-template-columns: 1fr; max-width: 320px;">
                            <div class="toggle-card" id="card-operator">
                                <span class="toggle-card-badge"></span>
                                <input type="checkbox" id="chk-operator">
                                <img src="_static/images/environment_builder_images/SMIA_operator_icon.svg" alt="SMIA Operator" class="card-local-img"
                                     onerror="this.style.display='none'">
                                <strong>SMIA Operator</strong>
                            </div>
                        </div>
                    </div>

                    <!-- Assets Simulator section — always visible (local AND docker/k8s) -->
                    <div id="assets-simulator-section" style="margin-top: 2rem; border-top: 1px solid var(--color-border); padding-top: 2rem;">
                        <label class="section-label">Assets Simulator</label>
                        <div class="env-grid" style="grid-template-columns: 1fr; max-width: 320px;">
                            <div class="toggle-card" id="card-assets-simulator">
                                <span class="toggle-card-badge"></span>
                                <input type="checkbox" id="chk-assets-simulator">
                                <svg viewBox="0 0 64 64" width="44" height="44" xmlns="http://www.w3.org/2000/svg" style="margin-bottom: 0.75rem;">
                                    <rect x="14" y="20" width="36" height="28" rx="4" fill="var(--color-brand-primary)" opacity="0.15" stroke="var(--color-brand-primary)" stroke-width="2"/>
                                    <circle cx="26" cy="32" r="4" fill="var(--color-brand-primary)"/>
                                    <circle cx="38" cy="32" r="4" fill="var(--color-brand-primary)"/>
                                    <line x1="32" y1="12" x2="32" y2="20" stroke="var(--color-brand-primary)" stroke-width="2"/>
                                    <circle cx="32" cy="10" r="3" fill="var(--color-brand-primary)" opacity="0.5"/>
                                    <path d="M24 42 h16" stroke="var(--color-brand-primary)" stroke-width="2.5" stroke-linecap="round"/>
                                </svg>
                                <strong>Assets Simulator HTTP</strong>
                            </div>
                        </div>
                        <div id="assets-simulator-config" style="display:none; margin-top: 1rem;">
                            <small style="display:block; margin-bottom: 0.75rem; color: var(--color-foreground-secondary);">
                                Configure the asset IDs for each category (comma-separated):
                            </small>
                            <div class="form-group">
                                <label>Production (Industrial) Assets</label>
                                <input type="text" id="sim-production-assets" class="smia-input"
                                       placeholder="e.g., industrial_robot_001,industrial_robot_002">
                            </div>
                            <div class="form-group">
                                <label>Mobile Assets</label>
                                <input type="text" id="sim-mobile-assets" class="smia-input"
                                       placeholder="e.g., mobile_robot_001,agv_002">
                            </div>
                            <div class="form-group">
                                <label>Human Assets</label>
                                <input type="text" id="sim-human-assets" class="smia-input"
                                       placeholder="e.g., human_worker_001">
                            </div>
                        </div>
                    </div>
                </div>

                <!-- ── STEP 4: Review & Generate (interactive) ── -->
                <div class="smia-step" id="step-4">
                    <h3>Review &amp; Generate</h3>
                    <p class="summary-intro">
                        Review your configuration below. Click <strong>Edit</strong> on any section to go back
                        and make changes, or proceed to download your environment package.
                    </p>
                    <div id="summary-content"></div>
                </div>

                <!-- Navigation Controls -->
                <div class="smia-controls" id="wizard-controls" style="display:none;">
                    <button id="btn-prev" class="smia-btn">← Previous</button>
                    <button id="btn-next" class="smia-btn primary">Next →</button>
                    <button id="btn-download" class="smia-btn primary" style="display:none;"><span>${ICONS.zipFile}</span> Download ZIP</button>
                </div>
            </div>
        `;
    },

    // ============================================================
    // EVENT BINDING
    // ============================================================

    bindEvents: function () {
        // Start wizard
        document.getElementById('btn-start').addEventListener('click', () => {
            this.state.step = 1;
            this.updateStepView();
        });

        // ── Step 1: Environment selection ──
        document.querySelectorAll('.env-card').forEach(card => {
            card.addEventListener('click', (e) => {
                document.querySelectorAll('.env-card').forEach(c => c.classList.remove('selected'));
                e.currentTarget.classList.add('selected');
                document.getElementById('env-error').style.display = 'none';
                this.state.envType = e.currentTarget.dataset.env;
                this.handleEnvChange(this.state.envType);
            });
        });

        // ── Step 1: Local scaffolding type ──
        document.querySelectorAll('[data-local-type]').forEach(card => {
            card.addEventListener('click', (e) => {
                document.querySelectorAll('[data-local-type]').forEach(c => c.classList.remove('selected'));
                e.currentTarget.classList.add('selected');
                this.state.localSettings.instanceType = e.currentTarget.dataset.localType;
            });
        });

        // ── Step 1: XMPP strategy ──
        document.querySelectorAll('[data-xmpp-strat]').forEach(card => {
            card.addEventListener('click', (e) => {
                document.querySelectorAll('[data-xmpp-strat]').forEach(c => c.classList.remove('selected'));
                e.currentTarget.classList.add('selected');
                const strategy = e.currentTarget.dataset.xmppStrat;
                this.state.xmpp.strategy = strategy;
                document.getElementById('xmpp-details-section').style.display =
                    (strategy === 'existing') ? 'block' : 'none';
            });
        });

        // ── Step 2: KB toggle card ──
        document.getElementById('card-kb').addEventListener('click', (e) => {
            if (e.target.type === 'checkbox') return;
            const chk = document.getElementById('chk-kb');
            chk.checked = !chk.checked;
            this.state.core.smiakb = chk.checked;
            this.updateToggleCardVisual('card-kb', this.state.core.smiakb);
            if (this.state.core.smiakb) {
                this._enableISM();
            } else {
                document.getElementById('ism-dependency-notice').style.display = 'none';
            }
        });

        document.getElementById('chk-kb').addEventListener('change', (e) => {
            this.state.core.smiakb = e.target.checked;
            this.updateToggleCardVisual('card-kb', this.state.core.smiakb);
            if (this.state.core.smiakb) {
                this._enableISM();
            } else {
                document.getElementById('ism-dependency-notice').style.display = 'none';
            }
        });

        // ── Step 2: ISM toggle card ──
        document.getElementById('card-ism').addEventListener('click', (e) => {
            if (e.target.type === 'checkbox') return;
            const chk = document.getElementById('chk-ism');
            if (chk.checked && this.state.core.smiakb) {
                this._showISMWarning();
                return;
            }
            chk.checked = !chk.checked;
            this.state.core.ism = chk.checked;
            this.updateToggleCardVisual('card-ism', this.state.core.ism);
            document.getElementById('ism-warning-notice').style.display = 'none';
        });

        document.getElementById('chk-ism').addEventListener('change', (e) => {
            if (!e.target.checked && this.state.core.smiakb) {
                e.target.checked = true;
                this._showISMWarning();
                return;
            }
            this.state.core.ism = e.target.checked;
            this.updateToggleCardVisual('card-ism', this.state.core.ism);
            document.getElementById('ism-warning-notice').style.display = 'none';
        });

        // ── Step 2: AAS selection ──
        document.querySelectorAll('[data-aas]').forEach(card => {
            card.addEventListener('click', (e) => {
                document.querySelectorAll('[data-aas]').forEach(c => c.classList.remove('selected'));
                e.currentTarget.classList.add('selected');
                const type = e.currentTarget.dataset.aas;
                this.state.core.aasServer.type = type;
                document.getElementById('aas-external-inputs').style.display =
                    (type === 'external') ? 'block' : 'none';
                document.getElementById('basyx-variant-selector').style.display =
                    (type === 'basyx') ? 'block' : 'none';
            });
        });

        // ── Step 2: BaSyx version selection (Go/Java) ──
        document.querySelectorAll('[data-basyx-variant]').forEach(card => {
            card.addEventListener('click', (e) => {
                document.querySelectorAll('[data-basyx-variant]').forEach(c => c.classList.remove('selected'));
                e.currentTarget.classList.add('selected');
                this.state.core.aasServer.basyxVariant = e.currentTarget.dataset.basyxVariant;
            });
        });

        // ── Step 3: Operator toggle card ──
        document.getElementById('card-operator').addEventListener('click', (e) => {
            if (e.target.type === 'checkbox') return;
            const chk = document.getElementById('chk-operator');
            chk.checked = !chk.checked;
            this.state.operator = chk.checked;
            this.updateToggleCardVisual('card-operator', this.state.operator);
        });

        document.getElementById('chk-operator').addEventListener('change', (e) => {
            this.state.operator = e.target.checked;
            this.updateToggleCardVisual('card-operator', this.state.operator);
        });

        // ── Step 3: Assets Simulator toggle card ──
        document.getElementById('card-assets-simulator').addEventListener('click', (e) => {
            if (e.target.type === 'checkbox') return;
            const chk = document.getElementById('chk-assets-simulator');
            chk.checked = !chk.checked;
            this.state.assetsSimulator.enabled = chk.checked;
            this.updateToggleCardVisual('card-assets-simulator', this.state.assetsSimulator.enabled);
            document.getElementById('assets-simulator-config').style.display = chk.checked ? 'block' : 'none';
        });

        document.getElementById('chk-assets-simulator').addEventListener('change', (e) => {
            this.state.assetsSimulator.enabled = e.target.checked;
            this.updateToggleCardVisual('card-assets-simulator', this.state.assetsSimulator.enabled);
            document.getElementById('assets-simulator-config').style.display = e.target.checked ? 'block' : 'none';
        });

        // ── Navigation ──
        document.getElementById('btn-next').addEventListener('click', () => this.nextStep());
        document.getElementById('btn-prev').addEventListener('click', () => this.prevStep());
        document.getElementById('btn-download').addEventListener('click', () => this.generateZip());

        // ── Step 3: Plan checkbox & asset button ──
        document.getElementById('btn-add-asset').addEventListener('click', () => this.addAssetUI());
        document.getElementById('chk-has-plan').addEventListener('change', (e) => {
            document.getElementById('plan-inputs').style.display = e.target.checked ? 'block' : 'none';
        });
    },

    // ── Private helpers ──────────────────────────────────────────

    _enableISM: function () {
        this.state.core.ism = true;
        document.getElementById('chk-ism').checked = true;
        this.updateToggleCardVisual('card-ism', true);
        document.getElementById('ism-dependency-notice').style.display = 'block';
        document.getElementById('ism-warning-notice').style.display = 'none';
    },

    _showISMWarning: function () {
        const el = document.getElementById('ism-warning-notice');
        el.style.display = 'block';
        setTimeout(() => { el.style.display = 'none'; }, 3000);
    },

    // ============================================================
    // ENV CHANGE HANDLER
    // ============================================================

    handleEnvChange: function (env) {
        const container = document.getElementById('dynamic-infra-options');
        const localGroup = document.getElementById('local-options-group');
        const dockerGroup = document.getElementById('container-xmpp-options');

        container.style.display = 'block';

        if (env === 'local') {
            localGroup.style.display = 'block';
            dockerGroup.style.display = 'none';
            this.state.xmpp.strategy = 'existing';
        } else {
            localGroup.style.display = 'none';
            dockerGroup.style.display = 'block';
            const selectedCard = document.querySelector('[data-xmpp-strat].selected');
            const strat = selectedCard ? selectedCard.dataset.xmppStrat : 'new';
            this.state.xmpp.strategy = strat;
            document.getElementById('xmpp-details-section').style.display =
                (strat === 'existing') ? 'block' : 'none';
        }
    },

    // ============================================================
    // VISUAL HELPERS
    // ============================================================

    updateToggleCardVisual: function (cardId, isActive) {
        const card = document.getElementById(cardId);
        card.classList.toggle('selected', isActive);
    },

    // ============================================================
    // NAVIGATION
    // ============================================================

    nextStep: function () {
        if (!this.validateStep(this.state.step)) return;
        this.captureStepData(this.state.step);

        // Local fast-track: Step 1 → Step 3 (skip Step 2)
        if (this.state.step === 1 && this.state.envType === 'local') {
            this.state.step = 3;
        } else {
            this.state.step++;
        }
        this.updateStepView();
    },

    prevStep: function () {
        // Local fast-track back: Step 3 → Step 1
        if (this.state.step === 3 && this.state.envType === 'local') {
            this.state.step = 1;
        } else if (this.state.step > 1) {
            this.state.step--;
        } else if (this.state.step === 1) {
            this.state.step = 0;
        }
        this.updateStepView();
    },

    /**
     * Navigate directly to a specific step (used by summary "Edit" buttons).
     */
    goToStep: function (targetStep) {
        this.state.step = targetStep;
        this.updateStepView();
    },

    validateStep: function (step) {
        if (step === 1 && !this.state.envType) {
            document.getElementById('env-error').style.display = 'block';
            return false;
        }
        return true;
    },

    updateStepView: function () {
        document.querySelectorAll('.smia-welcome-screen, .smia-step').forEach(el => {
            el.classList.remove('active');
        });

        if (this.state.step === 0) {
            document.getElementById('step-0').classList.add('active');
            document.getElementById('progress-bar-container').style.display = 'none';
            document.getElementById('wizard-controls').style.display = 'none';
            return;
        }

        document.getElementById(`step-${this.state.step}`).classList.add('active');
        document.getElementById('progress-bar-container').style.display = 'block';
        document.getElementById('wizard-controls').style.display = 'flex';

        // Progress bar
        let visualStep = this.state.step;
        let totalSteps = 4;
        if (this.state.envType === 'local') {
            if (this.state.step === 3) visualStep = 2;
            if (this.state.step === 4) visualStep = 3;
            totalSteps = 3;
        }
        document.getElementById('progress-fill').style.width =
            `${(visualStep / totalSteps) * 100}%`;

        // Step 3 per-mode adjustments
        if (this.state.step === 3) {
            const isLocal = (this.state.envType === 'local');
            document.getElementById('step-3-title').textContent = isLocal
                ? 'Add Asset File'
                : 'Step 3: Manufacturing assets';
            document.getElementById('step-3-intro-local').style.display = isLocal ? 'block' : 'none';
            document.getElementById('plan-card-container').style.display = isLocal ? 'none' : 'block';
            //document.getElementById('plan-card-container').style.display = 'block';
            document.getElementById('operator-section').style.display = 'block';
            document.getElementById('assets-simulator-section').style.display = 'block';

            const addBtn = document.getElementById('btn-add-asset');
            if (isLocal) {
                const existing = document.getElementById('assets-list').children.length;
                addBtn.textContent = '+ Add Asset (Optional)';
                addBtn.style.display = existing === 0 ? 'block' : 'none';
                if (existing === 0) this.addAssetUI();
            } else {
                addBtn.textContent = '+ Add Asset Instance';
                addBtn.style.display = 'block';
            }
        }

        // Button state
        const isLastStep = (this.state.step === 4);
        document.getElementById('btn-next').style.display = isLastStep ? 'none' : 'inline-block';
        document.getElementById('btn-download').style.display = isLastStep ? 'inline-flex' : 'none';
        document.getElementById('btn-prev').disabled = false;

        if (isLastStep) {
            this.generateSummary();
        }
    },

    // ============================================================
    // DATA CAPTURE
    // ============================================================

    captureStepData: function (step) {
        if (step === 1) {
            if (this.state.envType === 'local') {
                this.state.xmpp.domain = document.getElementById('xmpp-domain-local').value;
            } else {
                this.state.xmpp.domain = document.getElementById('xmpp-domain').value || 'localhost';
                this.state.xmpp.ip = document.getElementById('xmpp-ip').value || '127.0.0.1';
            }
        }

        if (step === 2) {
            if (this.state.core.aasServer.type === 'external') {
                this.state.core.aasServer.ip = document.getElementById('aas-ip').value;
            }
        }

        if (step === 3) {
            const planFileEl = document.getElementById('plan-file');
            this.state.plan.hasPlan = document.getElementById('chk-has-plan').checked;
            this.state.plan.jid = document.getElementById('plan-jid').value || 'smia-pe';
            this.state.plan.password = document.getElementById('plan-password').value || 'gcis1234';

            if (planFileEl.files.length > 0) {
                this.state.plan.file = planFileEl.files[0];
                this.state.plan.path = planFileEl.files[0].name;
            } else {
                this.state.plan.path = document.getElementById('plan-path').value;
            }

            this.state.operator = document.getElementById('chk-operator').checked;

            this.state.assetsSimulator.enabled = document.getElementById('chk-assets-simulator').checked;
            if (this.state.assetsSimulator.enabled) {
                this.state.assetsSimulator.productionAssets = document.getElementById('sim-production-assets').value;
                this.state.assetsSimulator.mobileAssets = document.getElementById('sim-mobile-assets').value;
                this.state.assetsSimulator.humanAssets = document.getElementById('sim-human-assets').value;
            }

            this.state.assets = [];
            document.querySelectorAll('#assets-list .asset-card').forEach(card => {
                const isExtended = card.querySelector('.chk-extended').checked;
                const fileInput = card.querySelector('.asset-file-input');
                let path = card.querySelector('.asset-id-input').value;
                let fileObj = null;

                if (fileInput.files.length > 0) {
                    fileObj = fileInput.files[0];
                    path = fileObj.name;
                }

                this.state.assets.push({
                    path: path,
                    file: fileObj,
                    isExtended: isExtended,
                    image: isExtended
                        ? card.querySelector('.asset-image-input').value
                        : 'smia/standard-asset:latest',
                    jid: card.querySelector('.agent-jid-input').value || `smia-${this.state.assets.length + 1}`,
                    password: card.querySelector('.asset-password-input').value || 'gcis1234'
                });
            });
        }
    },

    // ============================================================
    // INTERACTIVE SUMMARY (Step 4)
    // ============================================================

    generateSummary: function () {
        const s = this.state;
        let html = s.envType === 'local'
            ? this._buildSummaryLocal(s)
            : this._buildSummaryContainer(s);

        html += `<div class="summary-cta">
            <strong>Ready?</strong> Click <strong>Download ZIP</strong> below to generate your environment package.
        </div>`;

        document.getElementById('summary-content').innerHTML = html;
    },

    // ── Helpers ─────────────────────────────────────────────────

    _badge: function (text, colour) {
        return `<span class="summary-badge badge-${colour}">${text}</span>`;
    },

    _row: function (key, valHtml) {
        return `<div class="summary-row">
            <span class="summary-key">${key}</span>
            <span class="summary-val">${valHtml}</span>
        </div>`;
    },

    _summaryCard: function (titleIconSvg, titleText, editStep, bodyHtml, extraClass) {
        const editBtn = editStep !== null
            ? `<button class="summary-edit-btn" onclick="SMIA_Builder.goToStep(${editStep})">Edit</button>`
            : '';
        const cls = extraClass ? ` ${extraClass}` : '';
        return `<div class="summary-card${cls}">
            <div class="summary-card-header">
                <span class="summary-card-title">${titleIconSvg} ${titleText}</span>
                ${editBtn}
            </div>
            ${bodyHtml}
        </div>`;
    },

    // ── LOCAL summary (2 cards stacked) ─────────────────────────

    _buildSummaryLocal: function (s) {
        const infraRows =
            this._row('Environment', this._badge('Local (Python)', 'blue')) +
            this._row('Scaffolding', this._badge(s.localSettings.instanceType.toUpperCase(), 'orange')) +
            this._row('XMPP Domain', `<code class="summary-val">${s.xmpp.domain || '—'}</code>`);

        const infraCard = this._summaryCard(
            ICONS.summaryInfra, 'Base Environment', 1,
            `<div class="summary-card-body">${infraRows}</div>`
        );

        // Assets card (full-width for local too)
        const assetsCard = this._buildAssetsCard(s, 3);

        return `<div class="summary-grid-top">${infraCard}</div>
                <div class="summary-card-full-row">${assetsCard}</div>`;
    },

    // ── DOCKER/K8S summary ───────────────────────────────────────

    _buildSummaryContainer: function (s) {
        // Infrastructure card
        const envLabel = s.envType === 'docker' ? 'Docker Compose' : 'Kubernetes';
        const xmppVal = s.xmpp.strategy === 'new'
            ? this._badge('New Ejabberd', 'blue')
            : `${this._badge('Existing', 'orange')} <code class="summary-val">${s.xmpp.domain || '—'}</code>`;
        const infraRows =
            this._row('Environment', this._badge(envLabel, 'blue')) +
            this._row('XMPP Server', xmppVal) +
            (s.xmpp.strategy === 'existing'
                ? this._row('Server IP', `<code class="summary-val">${s.xmpp.ip || '—'}</code>`) : '');

        const infraCard = this._summaryCard(
            ICONS.summaryInfra, 'Base Environment', 1,
            `<div class="summary-card-body">${infraRows}</div>`
        );

        // Core Services card
        const aasLabels = { basyx: 'Deploy Basyx', external: 'Use Existing', none: 'None (File Mode)' };
        const aasBadgeClr = { basyx: 'blue', external: 'orange', none: 'gray' };
        const aasLabel = s.core.aasServer.type === 'basyx'
            ? `Deploy Basyx (${(s.core.aasServer.basyxVariant || 'go') === 'go' ? 'Go' : 'Java'})`
            : aasLabels[s.core.aasServer.type];
        const coreRows =
            this._row('SMIA-I KB',
                s.core.smiakb ? this._badge('Enabled', 'green') : this._badge('Disabled', 'gray')) +
            this._row('SMIA ISM',
                s.core.ism ? this._badge('Enabled', 'green') : this._badge('Disabled', 'gray')) +
            this._row('AAS Server',
                this._badge(aasLabel, aasBadgeClr[s.core.aasServer.type])) +
            (s.core.aasServer.type === 'external'
                ? this._row('AAS IP', `<code class="summary-val">${s.core.aasServer.ip || '—'}</code>`) : '');

        const coreCard = this._summaryCard(
            ICONS.summaryServices, 'Infrastructure Services', 2,
            `<div class="summary-card-body">${coreRows}</div>`
        );

        // Full-width Assets & Manufacturing card
        const assetsCard = this._buildAssetsCard(s, 3);

        return `<div class="summary-grid-top">${infraCard}${coreCard}</div>
                <div class="summary-card-full-row">${assetsCard}</div>`;
    },

    /**
     * Builds the full-width "Assets & Manufacturing" summary card.
     * Internally split into two sub-sections:
     *   1. Manufacturing Plan
     *   2. Production Assets  (+ Operator row at the bottom)
     *
     * @param {object} s    - SMIA_Builder.state
     * @param {number} step - step number for the Edit button
     */
    _buildAssetsCard: function (s, step) {
        const isLocal = (s.envType === 'local');

        // ── Sub-section 1: Manufacturing Plan ────────────────────
        let planSection = '';
        if (!isLocal) {
            const planVal = s.plan.hasPlan
                ? `${this._badge('Included', 'green')} ${s.plan.path ? `<small style="display:block; margin-top:0.4rem; font-weight:400; word-break: break-all;">${s.plan.path}</small>` : ''}`
                : this._badge('Not included', 'gray');

            planSection = `<div class="summary-subsection">
                <div class="summary-subsection-title">Manufacturing Plan</div>
                <div class="summary-row">
                    <span class="summary-key">CSS-enriched Plan</span>
                    <span class="summary-val">${planVal}</span>
                </div>
            </div>`;
        }

        // ── Sub-section 2: Production Assets ─────────────────────
        let assetItems = '';
        if (s.assets.length === 0) {
            assetItems = `<p class="summary-empty">No assets defined.</p>`;
        } else {
            const items = s.assets.map((a, i) => {
                const label = a.path || 'Unnamed asset';
                const extBadge = a.isExtended
                    ? ` <span class="summary-badge badge-orange" style="font-size:0.68rem;">Extended</span>`
                    : '';
                const imgNote = a.isExtended && a.image
                    ? `<small style="color:var(--color-foreground-secondary); display:block; margin-top:0.2rem; word-break: break-all;">${a.image}</small>`
                    : '';
                return `<li><span><strong>#${i + 1}</strong> — ${label}${extBadge}${imgNote}</span></li>`;
            }).join('');
            assetItems = `<ul class="summary-asset-list">${items}</ul>`;
        }

        // Operator row appended at bottom of assets sub-section
        const operatorRow = this._row(
            'SMIA Operator',
            s.operator ? this._badge('Enabled', 'green') : this._badge('Disabled', 'gray')
        );

        // Assets Simulator row
        const simulatorRow = this._row(
            'Assets Simulator',
            s.assetsSimulator.enabled ? this._badge('Enabled', 'green') : this._badge('Disabled', 'gray')
        );

        // Assets Simulator details (shown only when enabled)
        let simulatorDetails = '';
        if (s.assetsSimulator.enabled) {
            const simRows = [];
            if (s.assetsSimulator.productionAssets) simRows.push(this._row('Production', `<code class="summary-val">${s.assetsSimulator.productionAssets}</code>`));
            if (s.assetsSimulator.mobileAssets) simRows.push(this._row('Mobile', `<code class="summary-val">${s.assetsSimulator.mobileAssets}</code>`));
            if (s.assetsSimulator.humanAssets) simRows.push(this._row('Human', `<code class="summary-val">${s.assetsSimulator.humanAssets}</code>`));
            if (simRows.length > 0) simulatorDetails = simRows.join('');
        }

        const assetsSection = `<div class="summary-subsection">
            <div class="summary-subsection-title">Production Assets (${s.assets.length})</div>
            ${assetItems}
            <div style="margin-top: 0.75rem; padding-top: 0.6rem; border-top: 1px dashed var(--color-border); display: flex; flex-direction: column; gap: 0.2rem;">
                ${operatorRow}
                ${simulatorRow}
                ${simulatorDetails}
            </div>
        </div>`;

        // ── Card wrapper ──────────────────────────────────────────
        const bodyHtml = `<div class="summary-assets-body"${isLocal ? ' style="grid-template-columns: 1fr;"' : ''}>
            ${planSection}
            ${assetsSection}
        </div>`;

        return this._summaryCard(
            ICONS.summaryAssets, 'Manufacturing assets', step, bodyHtml
        );
    },

    // ============================================================
    // ZIP GENERATION
    // ============================================================

    generateZip: async function () {
        const zip = new JSZip();
        const s = this.state;

        const downloadBtn = document.getElementById('btn-download');
        const originalHTML = downloadBtn.innerHTML;
        downloadBtn.disabled = true;
        downloadBtn.innerHTML = '⏳ Generating...';

        try {
            if (s.envType === 'local') {
                // Local mode: fetch Python files from GitHub and build structured ZIP
                await this._buildLocalZip(zip, s);
            } else if (s.envType === 'k8s') {
                // Kubernetes mode: generate YAML Deployment manifests + deploy.sh
                await this._buildK8sZip(zip, s);
            } else {
                // Docker Compose mode: build docker-compose.yml from reference services
                const yamlContent = await this.buildDockerCompose();
                zip.file("docker-compose.yml", yamlContent);

                // Add ejabberd config when deploying a new XMPP server
                if (s.xmpp.strategy === 'new') {
                    const ejabberdContent = (typeof EJABBERD_YAML !== 'undefined' && EJABBERD_YAML)
                        ? EJABBERD_YAML
                        : '# ejabberd configuration\n# Could not load automatically. Please add ejabberd.yml manually.\n';
                    zip.folder('xmpp_server').file('ejabberd.yml', ejabberdContent);
                }

                // Add AAS model files into aas/ folder
                const aasFolder = zip.folder('aas');
                if (s.plan.hasPlan && s.plan.file) aasFolder.file(s.plan.file.name, s.plan.file);
                s.assets.forEach(asset => { if (asset.file) aasFolder.file(asset.file.name, asset.file); });

                // Download SMIA ISM AASX model from GitHub
                if (s.core.ism) {
                    const ismAasx = await this._fetchBinaryFile(GITHUB_URLS.ISM_AASX);
                    if (ismAasx) aasFolder.file('SMIA_InfrastructureServicesManager.aasx', ismAasx);
                }

                // Download SMIA Operator AASX model from GitHub
                if (s.operator) {
                    const operatorAasx = await this._fetchBinaryFile(GITHUB_URLS.OPERATOR_AASX);
                    if (operatorAasx) aasFolder.file('SMIA_operator.aasx', operatorAasx);
                }

                // Add BaSyx configuration files when deploying BaSyx (Java or Go variant)
                if (s.core.aasServer.type === 'basyx') {
                    const basyxFolder = zip.folder('basyx');
                    if ((s.core.aasServer.basyxVariant || 'go') === 'go') {
                        const rsaKey = (typeof BASYX_GO_RSA_KEY !== 'undefined' && BASYX_GO_RSA_KEY)
                            ? BASYX_GO_RSA_KEY
                            : '';
                        if (rsaKey) basyxFolder.file('rsa-key.pem', rsaKey);
                        basyxFolder.file('basyx-infra.yml', this._buildBasyxGoInfraYml());
                    } else {
                        basyxFolder.file('aas-env.properties', this._buildBasyxAasEnvProperties());
                        basyxFolder.file('aas-registry.yml', this._buildBasyxAasRegistryYml());
                        basyxFolder.file('sm-registry.yml', this._buildBasyxSmRegistryYml());
                    }
                }

                // README
                zip.file('README.md', this._buildContainerReadme(s));
            }

            const content = await zip.generateAsync({ type: "blob" });
            saveAs(content, `smia.zip`);
        } catch (err) {
            console.error('ZIP generation error:', err);
            alert('Error generating ZIP: ' + err.message);
        } finally {
            downloadBtn.disabled = false;
            downloadBtn.innerHTML = originalHTML;
        }
    },

    // ============================================================
    // LOCAL ZIP BUILDER (async)
    // ============================================================

    /**
     * Builds the full ZIP structure for Local (Python) mode.
     * Fetches launcher scripts from GitHub, applies substitutions,
     * and optionally adds the SMIA Operator repository.
     */
    _buildLocalZip: async function (zip, s) {
        const xmppDomain = (s.xmpp.domain) ? s.xmpp.domain : null;

        // ── Collect AASX file and JID/Password from assets or plan ──
        let aasxFile = null;
        let aasxFilename = null;
        let jid = '';
        let password = '';
        if (s.assets.length > 0) {
            const asset = s.assets[0];
            if (asset.file) {
                aasxFile = asset.file;
                aasxFilename = asset.file.name;
            } else if (asset.path) {
                aasxFilename = asset.path;
            }
            jid = asset.jid;
            password = asset.password;
        } else if (s.plan.hasPlan) {
            if (s.plan.file) {
                aasxFile = s.plan.file;
                aasxFilename = s.plan.file.name;
            } else if (s.plan.path) {
                aasxFilename = s.plan.path;
            }
            jid = s.plan.jid;
            password = s.plan.password;
        }

        // ── Add AASX file to aasx/ folder ──
        if (aasxFile) {
            zip.folder('aas').file(aasxFilename, aasxFile);
        }

        // ── Fetch and add Python launcher(s) ──
        const type = s.localSettings.instanceType;

        if (type === 'normal' || type === 'both') {
            const raw = await this._fetchTextFile(
                GITHUB_URLS.LAUNCHER, // Note: currently uses EXTENDED_LAUNCHER URL due to TODO
                `# Standard SMIA Launcher\n# Auto-generated by SMIA Environment Builder\n`
            );
            const modified = this._applyPythonModifications(raw, xmppDomain, aasxFilename, jid, password, true);
            zip.folder('src').file('launcher.py', modified);
        }

        if (type === 'extended' || type === 'both') {
            const raw = await this._fetchTextFile(
                GITHUB_URLS.EXTENDED_LAUNCHER,
                `# Extended SMIA Launcher\n# Auto-generated by SMIA Environment Builder\n`
            );
            const modified = this._applyPythonModifications(raw, xmppDomain, aasxFilename, jid, password, false);
            zip.folder('src_extended').file('extended_launcher.py', modified);
        }

        // ── Extended SMIA: add docker/ folder for the first extended+uploaded asset ──
        for (const asset of s.assets) {
            if (asset.isExtended && asset.file) {
                const dockerfile = await this._fetchTextFile(
                    GITHUB_URLS.DOCKERFILE,
                    `# Dockerfile for Extended SMIA\n# Auto-generated by SMIA Environment Builder\nFROM python:3.11-slim\nCOPY . /app\nWORKDIR /app\nRUN pip install --no-cache-dir smia\nCMD ["python", "main.py"]\n`
                );
                const dockerFolder = zip.folder('docker');
                dockerFolder.file('Dockerfile', dockerfile);

                const imageTag = asset.image || 'my-smia-extended:latest';
                dockerFolder.file('docker_build.sh',
                    `#!/bin/bash\n# Build Extended SMIA Docker image\n# Generated by SMIA Environment Builder\ndocker build -t ${imageTag} .\n`
                );
                break; // Only one docker/ folder regardless of how many extended assets exist
            }
        }

        // ── SMIA Operator: fetch repo archive and embed into ZIP ──
        if (s.operator) {
            await this._addOperatorToZip(zip, s);
        }

        // ── Assets Simulator: fetch project files and embed into ZIP ──
        if (s.assetsSimulator.enabled) {
            await this._addAssetsSimulatorToZip(zip, s);
        }

        // ── Fetch and add CSS-ontology-smia.owl ──
        const archiveFolder = zip.folder('smia_archive').folder('config');
        archiveFolder.folder('aas');
        const owlContent = await this._fetchTextFile(GITHUB_URLS.CSS_ONTOLOGY, '');
        if (owlContent) {
            archiveFolder.file('CSS-ontology-smia.owl', owlContent);
        }

        // ── README ──
        zip.file('README.md', this._buildLocalReadme(s, aasxFilename));
    },

    /**
     * Fetches a text file from a URL. Returns fallback string on any error.
     * @param {string} url
     * @param {string} fallback
     * @returns {Promise<string>}
     */
    _fetchTextFile: async function (url, fallback) {
        try {
            const response = await fetch(url);
            if (!response.ok) throw new Error(`HTTP ${response.status} for ${url}`);
            return await response.text();
        } catch (err) {
            console.warn(`[SMIA Builder] Could not fetch: ${url}`, err);
            return fallback || `# Could not fetch from:\n# ${url}\n# Please download this file manually.\n`;
        }
    },

    /**
     * Fetches a binary file from a URL.
     * Returns an ArrayBuffer suitable for JSZip, or null on error.
     * @param {string} url
     * @returns {Promise<ArrayBuffer|null>}
     */
    _fetchBinaryFile: async function (url) {
        try {
            const response = await fetch(url);
            if (!response.ok) throw new Error(`HTTP ${response.status} for ${url}`);
            return await response.arrayBuffer();
        } catch (err) {
            console.warn(`[SMIA Builder] Could not fetch binary: ${url}`, err);
            return null;
        }
    },

    /**
     * Fetches the Operator docker-compose.yml from GitHub and extracts
     * the 'smia-operator' service block.
     * @returns {Promise<string|null>}
     */
    _fetchOperatorService: async function () {
        try {
            const yamlText = await this._fetchTextFile(GITHUB_URLS.OPERATOR_DOCKER_COMPOSE, null);
            if (!yamlText) return null;
            let block = this._extractServiceBlock(yamlText, 'smia-operator');
            // Replace the placeholder AAS_MODEL_NAME with the actual filename
            if (block) {
                block = block.replace(
                    /AAS_MODEL_NAME=.*/,
                    'AAS_MODEL_NAME=SMIA_operator.aasx'
                );
            }
            return block;
        } catch (err) {
            console.warn('[SMIA Builder] Could not fetch Operator service definition', err);
            return null;
        }
    },

    /**
     * Applies XMPP domain and AASX path substitutions to Python source code.
     * - "<jid of agent>" → "<jid of agent>@<xmppDomain>" (when domain is set)
     * - "<path to the AAS model>" → "aasx/<aasxFilename>" (when AASX file uploaded)
     * @param {string} content
     * @param {string|null} xmppDomain
     * @param {string|null} aasxFilename
     * @returns {string}
     */
    /**
     * Applies XMPP domain and AASX path substitutions to Python source code.
     * @param {string} content
     * @param {string|null} xmppDomain
     * @param {string|null} aasxFilename
     * @param {string} jid
     * @param {string} password
     * @param {boolean} isNormal
     * @returns {string}
     */
    _applyPythonModifications: function (content, xmppDomain, aasxFilename, jid, password, isNormal) {
        let modified = content;

        if (jid) {
            const fullJid = xmppDomain ? `${jid}@${xmppDomain}` : jid;
            modified = modified.replace(/<jid of SMIA SPADE agent>/g, `'${fullJid}'`);
        } else if (xmppDomain) {
            modified = modified.replace(/<jid of SMIA SPADE agent>/g, `'agent@${xmppDomain}'`);
        }

        if (password) {
            modified = modified.replace(/<password of SMIA SPADE agent>/g, `'${password}'`);
        }

        if (aasxFilename) {
            modified = modified.replace(/<path to the AAS model>/g, `'../aas/${aasxFilename}'`);
        }

        if (isNormal) {
            modified = modified.replace(/ExtensibleSMIAAgent/g, 'SMIAAgent');
            modified = modified.replace(/extensible_smia_agent/g, 'smia_agent');
        }

        return modified;
    },

    /**
     * Fetches the SMIA Operator subfolder from the main repository and adds
     * its contents to the output ZIP under `smia_operator_agent/`, preserving
     * the internal directory structure.
     *
     * The operator lives at:
     *   {GITHUB_REPO}/{OPERATOR_SUBFOLDER}/
     *
     * Approach:
     *   1. GitHub Trees API (CORS-enabled) → full recursive tree of main repo as JSON
     *   2. Filter items to those whose path starts with OPERATOR_SUBFOLDER
     *   3. Fetch each file from raw.githubusercontent.com (CORS-enabled)
     *   4. Strip the OPERATOR_SUBFOLDER prefix so the ZIP entry is relative
     *      e.g. "additional_tools/extended_agents/smia_operator_agent/src/agent.py"
     *           → added as "smia_operator_agent/src/agent.py"
     *
     * @param {JSZip} zip
     * @param {object} s
     */
    _addOperatorToZip: async function (zip, s) {
        const targetFolder = zip.folder('smia_operator_agent');
        const prefix = GITHUB_URLS.OPERATOR_SUBFOLDER + '/';

        // ── Stage 1: Fetch the full repo tree and filter to the operator subfolder ──
        let operatorItems;
        try {
            const treeResp = await fetch(GITHUB_URLS.GITHUB_TREE);
            if (!treeResp.ok) throw new Error(`GitHub Trees API returned HTTP ${treeResp.status}`);

            const treeData = await treeResp.json();
            if (!treeData.tree || !Array.isArray(treeData.tree)) {
                throw new Error('Unexpected response format from GitHub Trees API');
            }

            if (treeData.truncated) {
                console.warn('[SMIA Builder] GitHub Trees API response was truncated. Some operator files may be missing.');
            }

            // Keep only file blobs whose path is inside the operator subfolder
            operatorItems = treeData.tree.filter(item =>
                item.type === 'blob' && item.path.startsWith(prefix)
            );

            if (operatorItems.length === 0) {
                throw new Error(`No files found under "${GITHUB_URLS.OPERATOR_SUBFOLDER}" in the repository tree.`);
            }
        } catch (err) {
            console.warn('[SMIA Builder] Could not fetch operator file tree:', err);
            targetFolder.file('README.md',
                `# SMIA Operator Agent\n\n` +
                `> ⚠️ Files could not be downloaded automatically.\n\n` +
                `**Reason:** ${err.message}\n\n` +
                `Please copy the contents of:\n` +
                `\`${GITHUB_URLS.OPERATOR_SUBFOLDER}/\`\n` +
                `from the SMIA repository into this folder.\n`
            );
            return;
        }

        // ── Stage 2: Fetch each file in parallel, strip the subfolder prefix ──
        let successCount = 0;
        let failCount = 0;

        const fetchPromises = operatorItems.map(item => {
            const rawUrl = `${GITHUB_URLS.OPERATOR_RAW_BASE}${item.path}`;
            // Strip "additional_tools/extended_agents/smia_operator_agent/" prefix
            const zipPath = item.path.slice(prefix.length);

            if (zipPath.endsWith('smia_operator_starter.py')) {
                return fetch(rawUrl)
                    .then(r => {
                        if (!r.ok) throw new Error(`HTTP ${r.status}`);
                        return r.text();
                    })
                    .then(text => {
                        let modifiedText = text.replace(/#\s*aas_model_path\s*=\s*'SMIA_Operator_article\.aasx'/g, "aas_model_path = 'SMIA_Operator_article.aasx'");
                        if (s && s.envType === 'local') {
                            const domainSuffix = s.xmpp.domain ? `@${s.xmpp.domain}` : '';
                            modifiedText = modifiedText.replace(
                                /(\s*)(smia_jid\s*=\s*os\.environ\.get\(['"][^'"]+['"]\))\s*\n\s*(smia_psswd\s*=\s*os\.environ\.get\(['"][^'"]+['"]\))/g,
                                `$1# $2\n$1# $3\n$1smia_jid = '<ADD HERE THE JID FOR SMIA OPERATOR AGENT>${domainSuffix}'\n$1smia_psswd = '<ADD HERE THE PASSWORD FOR SMIA OPERATOR AGENT>'`
                            );
                        }
                        targetFolder.file(zipPath, modifiedText);
                        successCount++;
                    })
                    .catch(err => {
                        console.warn(`[SMIA Builder] Failed to fetch string: ${item.path} — ${err.message}`);
                        failCount++;
                    });
            } else {
                return fetch(rawUrl)
                    .then(r => {
                        if (!r.ok) throw new Error(`HTTP ${r.status}`);
                        return r.arrayBuffer();
                    })
                    .then(data => {
                        targetFolder.file(zipPath, data);
                        successCount++;
                    })
                    .catch(err => {
                        console.warn(`[SMIA Builder] Failed to fetch: ${item.path} — ${err.message}`);
                        failCount++;
                    });
            }
        });

        await Promise.allSettled(fetchPromises);

        console.info(`[SMIA Builder] SMIA Operator: ${successCount} file(s) added, ${failCount} failed.`);

        if (successCount === 0) {
            targetFolder.file('README.md',
                `# SMIA Operator Agent\n\n` +
                `> ⚠️ All ${failCount} file download(s) failed.\n\n` +
                `This is usually caused by a network restriction or GitHub rate limiting.\n\n` +
                `Please copy the contents of:\n` +
                `\`${GITHUB_URLS.OPERATOR_SUBFOLDER}/\`\n` +
                `from the SMIA repository into this folder.\n`
            );
        }
    },

    /**
     * Builds the README.md content for Local (Python) mode.
     * @param {object} s  - SMIA_Builder.state
     * @param {string|null} aasxFilename
     * @returns {string}
     */
    _buildLocalReadme: function (s, aasxFilename) {
        const type = s.localSettings.instanceType;
        let md = `# SMIA Local Development Environment\n\n`;
        md += `> Generated by **SMIA Environment Builder**\n\n`;
        md += `## Configuration Summary\n\n`;
        md += `| Setting | Value |\n|---|---|\n`;
        md += `| Environment | Local (Python) |\n`;
        md += `| Scaffolding Type | ${type.charAt(0).toUpperCase() + type.slice(1)} |\n`;
        if (s.xmpp.domain) md += `| XMPP Domain | \`${s.xmpp.domain}\` |\n`;
        if (aasxFilename) md += `| AAS Model File | \`aasx/${aasxFilename}\` |\n`;
        if (s.operator) md += `| SMIA Operator | Enabled |\n`;
        if (s.assetsSimulator.enabled) md += `| Assets Simulator | Enabled |\n`;

        md += `\n## Directory Structure\n\n\`\`\`\n`;
        md += `smia_archive/\n  config/\n    aas/\n    CSS-ontology-smia.owl  ← CSS ontology file\n`;
        if (type === 'normal' || type === 'both') md += `src/\n  launcher.py          ← Standard SMIA launcher\n`;
        if (type === 'extended' || type === 'both') md += `src_extended/\n  extended_launcher.py ← Extended SMIA launcher\n`;
        if (aasxFilename) md += `aasx/\n  ${aasxFilename}  ← AAS model file\n`;
        if (s.assets.some(a => a.isExtended && a.file)) {
            md += `docker/\n  Dockerfile           ← Extended SMIA image definition\n  docker_build.sh      ← Build script\n`;
        }
        if (s.operator) md += `smia_operator_agent/ ← SMIA Operator dashboard\n`;
        if (s.assetsSimulator.enabled) md += `assets_simulator_http/ ← HTTP Assets Simulator\n`;
        md += `README.md\n\`\`\`\n`;

        md += `\n## Getting Started\n\n`;
        md += `### Prerequisites\n\n`;
        md += `- Python 3.10+\n`;
        md += `- \`pip install smia\`\n`;
        if (s.xmpp.domain) md += `- An XMPP server accessible at \`${s.xmpp.domain}\`\n`;

        md += `\n### Running\n\n`;
        if (type === 'normal' || type === 'both') {
            md += `**Standard SMIA:**\n\`\`\`bash\npython src/launcher.py\n\`\`\`\n\n`;
        }
        if (type === 'extended' || type === 'both') {
            md += `**Extended SMIA:**\n\`\`\`bash\npython src_extended/extended_launcher.py\n\`\`\`\n\n`;
        }
        if (s.assets.some(a => a.isExtended && a.file)) {
            const imageTag = s.assets.find(a => a.isExtended && a.file)?.image || 'my-smia-extended:latest';
            md += `**Build Extended Docker Image:**\n\`\`\`bash\ncd docker && bash docker_build.sh\n\`\`\`\n`;
            md += `*(This will build the image tagged as \`${imageTag}\`)*\n\n`;
        }

        if (s.operator) {
            md += `**SMIA Operator:**\n`;
            md += `> **Note:** Since you are running the SMIA Operator locally, you must manually specify the Agent JID and Password in \`smia_operator_agent/smia_operator_starter.py\`.\n\n`;
            md += `After starting the agent, the SMIA Operator web interface will be available at [http://127.0.0.1:10000/smia_operator](http://127.0.0.1:10000/smia_operator)\n\n`;
            md += `\`\`\`bash\ncd smia_operator_agent\npython smia_operator_starter.py\n\`\`\`\n\n`;
        }

        if (s.assetsSimulator.enabled) {
            md += `**Assets Simulator (HTTP):**\n`;
            md += `The Assets Simulator provides an HTTP interface to simulate manufacturing assets.\n\n`;
            md += `\`\`\`bash\ncd assets_simulator_http\npip install -r docker/requirements.txt\npython main.py\n\`\`\`\n\n`;
            md += `The simulator web interface will be available at [http://127.0.0.1:5000](http://127.0.0.1:5000)\n\n`;
        }

        md += `\n## Resources\n\n`;
        md += `- [SMIA GitHub Repository](https://github.com/OWNER/REPO)\n`;
        md += `- [SMIA Documentation (Read the Docs)](https://smia.readthedocs.io)\n`;
        if (s.operator) {
            md += `- [SMIA Operator Agent](https://github.com/extended_agents/smia_operator_agent)\n`;
        }
        return md;
    },

    // ============================================================
    // KUBERNETES ZIP BUILDER
    // ============================================================

    /**
     * Builds the full ZIP structure for Kubernetes mode.
     * Generates per-asset Deployment YAML manifests (NFS + subPath + readOnly),
     * a deploy.sh script for automated NFS + PV/PVC setup, and a K8s-specific README.
     *
     * @param {JSZip} zip - JSZip instance to populate
     * @param {object} s  - SMIA_Builder.state
     */
    _buildK8sZip: async function (zip, s) {
        const xmppDomain = s.xmpp.domain || 'localhost';
        const k8sFolder = zip.folder('kubernetes');
        const aasFolder = zip.folder('aas');

        // ── SMIA-I KB (Step 2): Deployment + NodePort Service ──
        if (s.core.smiakb) {
            k8sFolder.file('deploy-smia-i-kb.yaml', this._yamlK8sSmiaiKb());
            // NodePort Service to expose SMIA-I KB on the node
            k8sFolder.file('service-smia-i-kb.yaml', this._yamlK8sSmiaiKbService());
        }

        // ── SMIA ISM (Step 2): Deployment with env vars ──
        if (s.core.ism) {
            k8sFolder.file('deploy-smia-ism.yaml', this._yamlK8sSmiaIsm(xmppDomain));
            // Download the ISM AASX model from GitHub into aas/
            const ismAasx = await this._fetchBinaryFile(GITHUB_URLS.ISM_AASX);
            if (ismAasx) aasFolder.file('SMIA_InfrastructureServicesManager.aasx', ismAasx);
        }

        // ── Manufacturing Plan — smia-pe (Step 3) ──
        if (s.plan.hasPlan) {
            const planFileName = s.plan.file ? s.plan.file.name : (s.plan.path || 'plan.aasx');
            k8sFolder.file('deploy-smia-pe.yaml', this._yamlK8sSmiaPe(planFileName, xmppDomain, s.plan.jid, s.plan.password));
            k8sFolder.file('service-smia-pe.yaml', this._yamlK8sSmiaPeService());
            // Add the plan AAS file into aas/
            if (s.plan.file) aasFolder.file(s.plan.file.name, s.plan.file);
        }

        // ── Production Assets — smia-X (Step 3) ──
        // SMIA-I KB registration: only when both KB and ISM are enabled
        const kbRegistrationEnabled = !!(s.core.smiakb && s.core.ism);
        s.assets.forEach((asset, i) => {
            const index = i + 1;                         // 1-based index
            const deployYaml = this._yamlK8sDeployment(asset, index, xmppDomain, kbRegistrationEnabled);
            // Add each manifest inside the kubernetes/ directory
            k8sFolder.file(`deploy-smia-${index}.yaml`, deployYaml);
        });

        // ── SMIA Operator (Step 3) ──
        if (s.operator) {
            k8sFolder.file('deploy-smia-operator.yaml', this._yamlK8sSmiaOperator(xmppDomain));
            // Download the Operator AASX model from GitHub into aas/
            const operatorAasx = await this._fetchBinaryFile(GITHUB_URLS.OPERATOR_AASX);
            if (operatorAasx) aasFolder.file('SMIA_operator.aasx', operatorAasx);
        }

        // ── Assets Simulator (Step 3) ──
        if (s.assetsSimulator.enabled) {
            k8sFolder.file('deploy-assets-simulator.yaml', this._yamlK8sAssetsSimulator(s));
            k8sFolder.file('service-assets-simulator.yaml', this._yamlK8sAssetsSimulatorService());
        }

        // ── Add AAS model files from production assets into the aas/ folder ──
        s.assets.forEach(asset => { if (asset.file) aasFolder.file(asset.file.name, asset.file); });

        // ── Generate the automated deployment script ──
        zip.file('deploy.sh', this._buildDeployScript(s));

        // ── README ──
        zip.file('README.md', this._buildContainerReadme(s));
    },

    /**
     * Generates a Kubernetes Deployment YAML manifest for a single production asset.
     * Uses the NFS + subPath + readOnly strategy:
     *   - Mounts the PVC "nfs-aas-pvc" as the volume source.
     *   - Uses subPath to mount only the specific asset file.
     *   - Sets readOnly: true on the volumeMount.
     *
     * @param {object} asset      - Asset state { path, file, isExtended, image }
     * @param {number} index      - 1-based sequential index
     * @param {string} xmppDomain - XMPP domain for AGENT_ID
     * @param {boolean} kbRegistrationEnabled - Add SMIAI_KB_REGISTRATION when KB and ISM are enabled
     * @returns {string} Complete Deployment YAML as a string
     */
    _yamlK8sDeployment: function (asset, index, xmppDomain, kbRegistrationEnabled) {
        // Unique identifier for this asset: smia-1, smia-2, etc.
        const id = `smia-${index}`;

        // Docker image: custom image for Extended SMIA, default otherwise
        const image = (asset.isExtended && asset.image)
            ? asset.image
            : 'ekhurtado/smia:latest-alpine';

        // The AAS model filename (from uploaded file or manual path)
        const aasModelName = asset.file ? asset.file.name : (asset.path || 'model.aasx');

        // ── Build the Deployment YAML string ──
        // IMPORTANT: YAML indentation is strictly 2 spaces per level.
        // The volumeMount uses subPath to mount only the specific file,
        // and readOnly: true to prevent accidental writes from the container.
        // SMIA-I KB registration: only when both KB and ISM are enabled
        const kbRegistrationBlock = kbRegistrationEnabled
            ? `            # SMIAI_KB_REGISTRATION: register asset in SMIA-I KB via SMIA ISM
            - name: SMIAI_KB_REGISTRATION
              value: "TRUE"
`
            : '';
        const yaml =
            `apiVersion: apps/v1
kind: Deployment
metadata:
  name: ${id}
  labels:
    app: ${id}
spec:
  replicas: 1
  selector:
    matchLabels:
      app: ${id}
  template:
    metadata:
      labels:
        app: ${id}
    spec:
      containers:
        - name: ${id}
          image: ${image}
          env:
            # AAS_MODEL_NAME: the exact filename of the AAS model for this asset
            - name: AAS_MODEL_NAME
              value: "${aasModelName}"
            # AGENT_ID: unique agent identifier with the XMPP domain
            - name: AGENT_ID
              value: "${asset.jid}@${xmppDomain}"
            # AGENT_PSSWD: default agent password
            - name: AGENT_PSSWD
              value: "${asset.password}"
${kbRegistrationBlock}          volumeMounts:
            # Mount only the specific AAS file via subPath (NFS-backed PVC)
            - name: nfs-aas-volume
              mountPath: /smia_archive/config/aas/${aasModelName}
              subPath: ${aasModelName}
              readOnly: true
      volumes:
        # Reference the shared NFS PersistentVolumeClaim
        - name: nfs-aas-volume
          persistentVolumeClaim:
            claimName: nfs-aas-pvc
`;
        return yaml;
    },

    /**
     * Generates a Kubernetes Deployment YAML for the SMIA-I KB service.
     * Uses image "ekhurtado/smia-tools:latest-smia-i-kb".
     * No AAS volume mount needed — this is a standalone knowledge base service.
     *
     * @returns {string} Deployment YAML
     */
    _yamlK8sSmiaiKb: function () {
        // SMIA-I KB Deployment: simple stateless service, no env vars required
        return `apiVersion: apps/v1
kind: Deployment
metadata:
  name: smia-i-kb
  labels:
    app: smia-i-kb
spec:
  replicas: 1
  selector:
    matchLabels:
      app: smia-i-kb
  template:
    metadata:
      labels:
        app: smia-i-kb
    spec:
      containers:
        - name: smia-i-kb
          image: ekhurtado/smia-tools:latest-smia-i-kb
          ports:
            - containerPort: 8080
`;
    },

    /**
     * Generates a Kubernetes Service YAML (NodePort) to expose SMIA-I KB.
     * Maps port 8090 → targetPort 8080, exposed on nodePort 31080.
     *
     * @returns {string} Service YAML
     */
    _yamlK8sSmiaiKbService: function () {
        // NodePort Service: exposes SMIA-I KB outside the cluster
        // so that other SMIA agents (e.g. SMIA ISM) can reach it.
        return `apiVersion: v1
kind: Service
metadata:
  name: smia-i-kb
spec:
  type: NodePort
  selector:
    app: smia-i-kb
  ports:
    - name: "8090"
      port: 8090
      targetPort: 8080
      nodePort: 31080
`;
    },

    /**
     * Generates a Kubernetes Deployment YAML for SMIA ISM.
     * Uses image "ekhurtado/smia-tools:latest-smia-ism" and includes
     * environment variables for AAS model, agent identity, and KB connection.
     *
     * @param {string} xmppDomain - XMPP domain from Step 1
     * @returns {string} Deployment YAML
     */
    _yamlK8sSmiaIsm: function (xmppDomain) {
        // The AAS model filename matches the one downloaded from GITHUB_URLS.ISM_AASX
        const aasModelName = 'SMIA_InfrastructureServicesManager.aasx';

        // SMIA ISM Deployment with NFS volume mount + env vars including KB URL
        return `apiVersion: apps/v1
kind: Deployment
metadata:
  name: smia-ism
  labels:
    app: smia-ism
spec:
  replicas: 1
  selector:
    matchLabels:
      app: smia-ism
  template:
    metadata:
      labels:
        app: smia-ism
    spec:
      containers:
        - name: smia-ism
          image: ekhurtado/smia-tools:latest-smia-ism
          env:
            # AAS_MODEL_NAME: ISM AAS model file (fetched from GitHub)
            - name: AAS_MODEL_NAME
              value: "${aasModelName}"
            # AGENT_ID: ISM agent identifier with user-configured XMPP domain
            - name: AGENT_ID
              value: "smia-ism@${xmppDomain}"
            # AGENT_PSSWD: default agent password
            - name: AGENT_PSSWD
              value: "gcis1234"
            # SMIA_KB_IP: URL to reach SMIA-I KB via the NodePort Service
            - name: SMIA_KB_IP
              value: "http://smia-i-kb:31080"
          volumeMounts:
            # Mount the ISM model file via subPath (NFS-backed PVC)
            - name: nfs-aas-volume
              mountPath: /smia_archive/config/aas/${aasModelName}
              subPath: ${aasModelName}
              readOnly: true
      volumes:
        - name: nfs-aas-volume
          persistentVolumeClaim:
            claimName: nfs-aas-pvc
`;
    },

    /**
     * Generates a Kubernetes Deployment YAML for the Manufacturing Plan (smia-pe).
     * Uses image "ekhurtado/smia-tools:latest-smia-pe".
     *
     * @param {string} planFileName - Name of the plan AAS model file
     * @param {string} xmppDomain   - XMPP domain from Step 1
     * @param {string} jid          - The JID for the PE agent
     * @param {string} password     - The password for the PE agent
     * @returns {string} Deployment YAML
     */
    _yamlK8sSmiaPe: function (planFileName, xmppDomain, jid, password) {
        // Manufacturing Plan Deployment: uses the plan file as AAS model
        return `apiVersion: apps/v1
kind: Deployment
metadata:
  name: smia-pe
  labels:
    app: smia-pe
spec:
  replicas: 1
  selector:
    matchLabels:
      app: smia-pe
  template:
    metadata:
      labels:
        app: smia-pe
    spec:
      containers:
        - name: smia-pe
          image: ekhurtado/smia-tools:latest-smia-pe
          ports:
            - containerPort: 10000
          env:
            # AAS_MODEL_NAME: the manufacturing plan AAS file
            - name: AAS_MODEL_NAME
              value: "${planFileName}"
            # AGENT_ID: PE agent identifier with user-configured XMPP domain
            - name: AGENT_ID
              value: "${jid}@${xmppDomain}"
            # AGENT_PSSWD: default agent password
            - name: AGENT_PSSWD
              value: "${password}"
          volumeMounts:
            # Mount the plan file via subPath (NFS-backed PVC)
            - name: nfs-aas-volume
              mountPath: /smia_archive/config/aas/${planFileName}
              subPath: ${planFileName}
              readOnly: true
      volumes:
        - name: nfs-aas-volume
          persistentVolumeClaim:
            claimName: nfs-aas-pvc
`;
    },

    /**
     * Generates a Kubernetes Service YAML (NodePort) to expose SMIA PE.
     * Maps external port 10010 → container targetPort 10000, exposed on nodePort 31010.
     *
     * @returns {string} Service YAML
     */
    _yamlK8sSmiaPeService: function () {
        return `apiVersion: v1
kind: Service
metadata:
  name: smia-pe
spec:
  type: NodePort
  selector:
    app: smia-pe
  ports:
    - name: "10010"
      port: 10010
      targetPort: 10000
      nodePort: 31010
`;
    },

    /**
     * Generates a Kubernetes Deployment YAML for the SMIA Operator.
     * Uses image "ekhurtado/smia-tools:latest-smia-ism".
     * The operator AASX model is fetched from GITHUB_URLS.OPERATOR_AASX.
     *
     * @param {string} xmppDomain - XMPP domain from Step 1
     * @returns {string} Deployment YAML
     */
    _yamlK8sSmiaOperator: function (xmppDomain) {
        // The AAS model filename matches the one downloaded from GITHUB_URLS.OPERATOR_AASX
        const aasModelName = 'SMIA_operator.aasx';

        // SMIA Operator Deployment with NFS volume mount
        return `apiVersion: apps/v1
kind: Deployment
metadata:
  name: smia-operator
  labels:
    app: smia-operator
spec:
  replicas: 1
  selector:
    matchLabels:
      app: smia-operator
  template:
    metadata:
      labels:
        app: smia-operator
    spec:
      containers:
        - name: smia-operator
          image: ekhurtado/smia-tools:latest-smia-operator
          env:
            # AAS_MODEL_NAME: Operator AAS model file (fetched from GitHub)
            - name: AAS_MODEL_NAME
              value: "${aasModelName}"
            # AGENT_ID: Operator agent identifier with user-configured XMPP domain
            - name: AGENT_ID
              value: "smia-operator@${xmppDomain}"
            # AGENT_PSSWD: default agent password
            - name: AGENT_PSSWD
              value: "gcis1234"
          volumeMounts:
            # Mount the Operator model file via subPath (NFS-backed PVC)
            - name: nfs-aas-volume
              mountPath: /smia_archive/config/aas/${aasModelName}
              subPath: ${aasModelName}
              readOnly: true
      volumes:
        - name: nfs-aas-volume
          persistentVolumeClaim:
            claimName: nfs-aas-pvc
`;
    },

    /**
     * Generates the deploy.sh Bash script for automated Kubernetes deployment.
     * The script performs three main tasks:
     *   1. Configures and starts an NFS server on the local machine (Ubuntu/Debian),
     *      exporting the ./aas directory.
     *   2. Creates the NFS PersistentVolume and PersistentVolumeClaim ("nfs-aas-pvc")
     *      in Kubernetes via kubectl.
     *   3. Deploys all generated manifests from the kubernetes/ directory.
     *
     * @param {object} s - SMIA_Builder.state
     * @returns {string} Complete Bash script content
     */
    _buildDeployScript: function (s) {
        // ── Interpolate the Bash script as a JS template literal ──
        // Each section is clearly commented for maintainability.
        const script =
            `#!/bin/bash
# ============================================================
# SMIA Kubernetes Deployment Script
# Generated by SMIA Environment Builder
# ============================================================
# This script:
#   1. Installs and configures an NFS server (Ubuntu/Debian)
#   2. Creates PersistentVolume + PersistentVolumeClaim in K8s
#   3. Deploys all SMIA agent manifests
# ============================================================

set -euo pipefail

# ── Resolve the absolute path of the aas/ directory ──
# The NFS export requires an absolute path; we derive it from
# the script's own location so it works regardless of where
# the user unpacked the ZIP.
SCRIPT_DIR="$(cd "$(dirname "\${BASH_SOURCE[0]}")" && pwd)"
AAS_DIR="\${SCRIPT_DIR}/aas"

echo "==> AAS directory: \${AAS_DIR}"

# ── Step 1: Install and configure the NFS server ──
# Installs nfs-kernel-server (idempotent via apt),
# adds the aas directory to /etc/exports, and restarts the service.
echo "==> Installing NFS server..."
sudo apt-get update -qq && sudo apt-get install -y -qq nfs-kernel-server

# Add the export entry if it does not already exist
if ! grep -q "\${AAS_DIR}" /etc/exports; then
  echo "\${AAS_DIR} *(rw,sync,no_subtree_check,no_root_squash)" | sudo tee -a /etc/exports
fi

# Apply the new exports and restart the NFS service
sudo exportfs -a
sudo systemctl restart nfs-kernel-server
echo "==> NFS server configured and running."

# ── Step 2: Detect local IP for the NFS PersistentVolume ──
LOCAL_IP="$(hostname -I | awk '{print $1}')"
echo "==> Detected local IP: \${LOCAL_IP}"

# ── Step 3: Create PersistentVolume and PersistentVolumeClaim ──
# Uses a heredoc piped into kubectl to create the NFS-backed
# PV and the corresponding PVC ("nfs-aas-pvc").
echo "==> Creating NFS PersistentVolume and PersistentVolumeClaim..."
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: PersistentVolume
metadata:
  name: nfs-aas-pv
spec:
  capacity:
    storage: 1Gi
  accessModes:
    - ReadOnlyMany
  nfs:
    server: \${LOCAL_IP}
    path: \${AAS_DIR}
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: nfs-aas-pvc
spec:
  accessModes:
    - ReadOnlyMany
  resources:
    requests:
      storage: 1Gi
  volumeName: nfs-aas-pv
EOF

echo "==> PV and PVC created successfully."

# ── Step 4: Deploy all Kubernetes manifests ──
# Applies every YAML file inside the kubernetes/ directory.
echo "==> Deploying SMIA agent manifests..."
kubectl apply -f kubernetes/

echo "============================================================"
echo "  SMIA Kubernetes deployment complete!"
echo "  Assets deployed: ${s.assets.length}"
echo "============================================================"
`;
        return script;
    },

    // ============================================================
    // DOCKER COMPOSE BUILDER
    // ============================================================

    /**
     * Returns the BaSyx Java variant docker-compose YAML content.
     * Reads from the global constant INFRA_BASYX_JAVA_YAML
     * (defined in infra-docker-compose-data.js, loaded via <script> tag).
     * @returns {string|null}
     */
    _getBasyxJavaYaml: function () {
        if (typeof INFRA_BASYX_JAVA_YAML !== 'undefined' && INFRA_BASYX_JAVA_YAML) {
            return INFRA_BASYX_JAVA_YAML;
        }
        console.warn('[SMIA Builder] INFRA_BASYX_JAVA_YAML not found. Ensure infra-docker-compose-data.js is loaded.');
        return null;
    },

    /**
     * Returns the BaSyx Go variant docker-compose YAML content.
     * Reads from the global constant INFRA_BASYX_GO_YAML
     * (defined in infra-docker-compose-data.js, loaded via <script> tag).
     * @returns {string|null}
     */
    _getBasyxGoYaml: function () {
        if (typeof INFRA_BASYX_GO_YAML !== 'undefined' && INFRA_BASYX_GO_YAML) {
            return INFRA_BASYX_GO_YAML;
        }
        console.warn('[SMIA Builder] INFRA_BASYX_GO_YAML not found. Ensure infra-docker-compose-data.js is loaded.');
        return null;
    },

    /**
     * Returns the Ejabberd XMPP server docker-compose YAML content.
     * Reads from the global constant INFRA_XMPP_YAML
     * (defined in infra-docker-compose-data.js, loaded via <script> tag).
     * @returns {string|null}
     */
    _getXmppYaml: function () {
        if (typeof INFRA_XMPP_YAML !== 'undefined' && INFRA_XMPP_YAML) {
            return INFRA_XMPP_YAML;
        }
        console.warn('[SMIA Builder] INFRA_XMPP_YAML not found. Ensure infra-docker-compose-data.js is loaded.');
        return null;
    },

    /**
     * Returns the SMIA infrastructure docker-compose YAML content
     * (smia-ism service + smia-i-kb template).
     * Reads from the global constant INFRA_SMIA_YAML
     * (defined in infra-docker-compose-data.js, loaded via <script> tag).
     * @returns {string|null}
     */
    _getSmiaYaml: function () {
        if (typeof INFRA_SMIA_YAML !== 'undefined' && INFRA_SMIA_YAML) {
            return INFRA_SMIA_YAML;
        }
        console.warn('[SMIA Builder] INFRA_SMIA_YAML not found. Ensure infra-docker-compose-data.js is loaded.');
        return null;
    },

    /**
     * Builds the smia-i-kb service block, parametrizing the BaSyx endpoint
     * and dependency according to the selected BaSyx variant.
     * @param {string} basyxVariant - 'go' | 'java'
     * @param {string} aasType - 'basyx' | 'external' | 'none'
     * @returns {string|null}
     */
    _buildSmiaIKbBlock: function (basyxVariant, aasType) {
        const smiaYaml = this._getSmiaYaml() || '';
        const template = this._extractServiceBlock(smiaYaml, 'smia-i-kb');
        if (!template) return null;
        const isGo = aasType === 'basyx' && (basyxVariant || 'go') === 'go';
        const envUrl = isGo ? 'http://aas-environment:8082' : 'http://aas-env:8081';
        const envService = isGo ? 'aas-environment' : 'aas-env';
        return template.split('__AAS_ENV_URL__').join(envUrl).split('__AAS_ENV_SERVICE__').join(envService);
    },

    /**
     * Extracts a single top-level service block from the infrastructure YAML.
     * Looks for a line matching `<serviceName>:` at root indentation and
     * collects all subsequent deeper-indented lines until the next sibling key.
     *
     * Handles YAML files where services may sit at indent 0 (local infra data)
     * OR under a `services:` key at indent 2 (GitHub docker-compose files).
     *
     * Trailing blank / comment lines are buffered and only flushed if the
     * block continues — this prevents absorbing decorative section headers
     * that belong to the next service group.
     *
     * @param {string} yamlText - Full YAML text content
     * @param {string} serviceName - Service name to extract (e.g. 'xmpp-server')
     * @returns {string|null} The service block re-indented under `services:`, or null
     */
    _extractServiceBlock: function (yamlText, serviceName) {
        const lines = yamlText.split(/\r?\n/);
        let capturing = false;
        let blockLines = [];
        let pendingLines = [];           // buffer for trailing blank / comment lines
        let serviceIndent = 0;           // indent level of the matched service name
        const servicePattern = new RegExp(`^${serviceName}\\s*:`);

        for (const line of lines) {
            if (!capturing) {
                // Match service name at any root-like indentation (0 or 2 spaces)
                if (servicePattern.test(line.trimStart()) &&
                    (line.startsWith(serviceName) || line.match(/^\s{0,2}\S/))) {
                    capturing = true;
                    serviceIndent = line.length - line.trimStart().length;
                    blockLines.push(`  ${serviceName}:`);
                }
            } else {
                const trimmed = line.trimStart();
                const indent = line.length - trimmed.length;

                // Blank lines or comment lines: buffer them instead of adding directly.
                // They will be flushed only if the block continues on the next real line.
                if (trimmed === '' || trimmed.startsWith('#')) {
                    pendingLines.push(`  ${line}`);
                    continue;
                }

                // A non-blank, non-comment line at the same or lesser indent as the
                // service name means we've reached a sibling key → stop capturing.
                if (indent <= serviceIndent) {
                    break;
                }

                // This line belongs to the current service: flush any buffered
                // blank / comment lines, then add this line.
                if (pendingLines.length > 0) {
                    blockLines.push(...pendingLines);
                    pendingLines = [];
                }

                // Re-indent: add 2 spaces prefix for nesting under `services:`
                blockLines.push(`  ${line}`);
            }
        }

        // Remove trailing blank lines (should already be clean, but just in case)
        while (blockLines.length > 0 && blockLines[blockLines.length - 1].trim() === '') {
            blockLines.pop();
        }

        return blockLines.length > 1 ? blockLines.join('\n') + '\n' : null;
    },

    /**
     * Builds the full docker-compose.yml content.
     * Combines the per-domain service definitions from infra-docker-compose-data.js
     * (BaSyx Java/Go, XMPP, SMIA) according to the selected configuration.
     * Dynamic services (smia-X assets, smia-pe) are generated programmatically.
     * When XMPP strategy is 'existing', injects extra_hosts into every service.
     * Async because the Operator service definition is fetched from GitHub.
     */
    buildDockerCompose: async function () {
        const s = this.state;
        const I = (n) => '  '.repeat(n);  // indentation helper
        const xmppDomain = s.xmpp.strategy === 'new' ? 'ejabberd' : (s.xmpp.domain || 'localhost');
        const basyxVariant = s.core.aasServer.basyxVariant || 'go';

        // Collect all service blocks
        const services = [];

        // ── XMPP Server (Deploy new) ──
        if (s.xmpp.strategy === 'new') {
            const block = this._extractServiceBlock(this._getXmppYaml() || '', 'xmpp-server');
            if (block) {
                services.push(
                    `  # ----------------------------------------\n` +
                    `  # XMPP Server (Ejabberd)\n` +
                    `  # ----------------------------------------\n` +
                    block
                );
            }
        }

        // ── BaSyx AAS Infrastructure (Deploy Basyx) — Java or Go variant ──
        if (s.core.aasServer.type === 'basyx') {
            services.push(
                `  # ----------------------------------------\n` +
                `  # AAS Infrastructure services (from BaSyx ${basyxVariant === 'go' ? 'Go' : 'Java'})\n` +
                `  # ----------------------------------------`
            );
            if (basyxVariant === 'go') {
                const goYaml = this._getBasyxGoYaml() || '';
                for (const svc of ['aas-environment', 'db', 'basyx_configuration', 'aas-ui']) {
                    const block = this._extractServiceBlock(goYaml, svc);
                    if (block) services.push(block);
                }
            } else {
                const javaYaml = this._getBasyxJavaYaml() || '';
                for (const svc of ['aas-env', 'aas-registry', 'sm-registry', 'mongo', 'aas-web-ui']) {
                    const block = this._extractServiceBlock(javaYaml, svc);
                    if (block) services.push(block);
                }
            }
        }

        // ── SMIA-I KB — BaSyx endpoint parametrized per variant ──
        if (s.core.smiakb) {
            const block = this._buildSmiaIKbBlock(basyxVariant, s.core.aasServer.type);
            if (block) services.push(block);
        }

        // ── SMIA ISM ──
        if (s.core.ism) {
            const block = this._extractServiceBlock(this._getSmiaYaml() || '', 'smia-ism');
            if (block) services.push(block);
        }

        // Whether the user chose to deploy a new XMPP server (ejabberd container)
        const xmppNew = s.xmpp.strategy === 'new';
        // Whether SMIA ISM is enabled (agents must depend on it)
        const ismEnabled = !!s.core.ism;
        // Whether SMIA-I KB registration is required (both KB and ISM enabled)
        const kbRegistrationEnabled = !!(s.core.smiakb && s.core.ism);

        // ── Dynamic services section header ──
        const hasDynamic = s.plan.hasPlan || s.assets.length > 0 || s.operator;
        if (hasDynamic) {
            services.push(
                `  # ----------------------------------------\n` +
                `  # SMIA Agents\n` +
                `  # ----------------------------------------`
            );
        }

        // ── Manufacturing Plan (smia-pe) ──
        if (s.plan.hasPlan) {
            services.push(this._yamlSmiaPe(I, s, xmppDomain, xmppNew, ismEnabled));
        }

        // ── Production Assets (smia-X) ──
        s.assets.forEach((asset, i) => {
            services.push(this._yamlSmiaAsset(I, asset, i + 1, xmppDomain, xmppNew, ismEnabled, kbRegistrationEnabled));
        });

        // ── SMIA Operator — fetched from GitHub docker-compose.yml ──
        if (s.operator) {
            const operatorBlock = await this._fetchOperatorService();
            if (operatorBlock) services.push(operatorBlock);
        }

        // ── Assets Simulator HTTP ──
        if (s.assetsSimulator.enabled) {
            services.push(
                `  # ----------------------------------------\n` +
                `  # Assets Simulator (HTTP)\n` +
                `  # ----------------------------------------`
            );
            services.push(this._yamlAssetsSimulator(I, s));
        }

        // ── Inject extra_hosts when using existing XMPP server ──
        let serviceBlocks;
        if (s.xmpp.strategy === 'existing' && s.xmpp.domain && s.xmpp.ip) {
            serviceBlocks = services.map(block =>
                this._injectExtraHosts(block, I, s.xmpp.domain, s.xmpp.ip)
            );
        } else {
            serviceBlocks = services;
        }

        let yaml = `services:\n`;
        yaml += serviceBlocks.join('\n');
        return yaml;
    },

    // ── Dynamic service YAML builders ──────────────────────────────

    /**
     * Manufacturing Plan service (smia-pe).
     * Uses a dedicated image and includes the plan file as AAS_MODEL_NAME.
     */
    _yamlSmiaPe: function (I, s, xmppDomain, xmppNew, ismEnabled) {
        const aasModelName = s.plan.path || s.plan.file?.name || 'plan.aasx';

        let safeJid = (s.plan.jid || 'smia-pe').toLowerCase().replace(/[^a-z0-9_.-]/g, '');

        let yaml =
            `${I(1)}${'smia-pe-' + safeJid}:\n` +
            `${I(2)}image: ekhurtado/smia-tools:latest-smia-pe\n` +
            `${I(2)}container_name: ${'smia-pe-' + safeJid}\n` +
            `${I(2)}environment:\n` +
            `${I(3)}- AAS_MODEL_NAME=${aasModelName}\n` +
            `${I(3)}- AGENT_ID=${safeJid}@${xmppDomain}\n` +
            `${I(3)}- AGENT_PSSWD=${s.plan.password}\n` +
            `${I(2)}ports:\n` +
            `${I(3)}- "10010:10000"\n` +
            `${I(2)}volumes:\n` +
            `${I(3)}- ./aas:/smia_archive/config/aas\n`;

        // Add depends_on block for XMPP server and/or SMIA ISM
        if (xmppNew || ismEnabled) {
            yaml += `${I(2)}depends_on:\n`;
            if (xmppNew) {
                yaml +=
                    `${I(3)}xmpp-server:\n` +
                    `${I(4)}condition: service_healthy\n`;
            }
            if (ismEnabled) {
                yaml +=
                    `${I(3)}smia-ism:\n` +
                    `${I(4)}condition: service_healthy\n`;
            }
        }

        return yaml;
    },

    /**
     * Production asset service (smia-X).
     * - If Extended SMIA is selected, uses the user-specified Docker image.
     * - If the user entered an AAS ID (text input), adds AAS_ID env var.
     * - If the user uploaded a file, uses AAS_MODEL_NAME with the filename.
     *
     * @param {Function} I   - Indentation helper
     * @param {object} asset - Asset state object { path, file, isExtended, image }
     * @param {number} index - 1-based asset index
     * @param {string} xmppDomain - XMPP domain for AGENT_ID
     * @param {boolean} kbRegistrationEnabled - Add SMIAI_KB_REGISTRATION when KB and ISM are enabled
     */
    _yamlSmiaAsset: function (I, asset, index, xmppDomain, xmppNew, ismEnabled, kbRegistrationEnabled) {
        const serviceName = (asset.jid || `smia-${index}`).toLowerCase().replace(/[^a-z0-9_.-]/g, '');

        const dockerImage = asset.isExtended && asset.image
            ? asset.image
            : 'ekhurtado/smia:latest-alpine';

        let envVars = '';

        // If the user uploaded a file, use AAS_MODEL_NAME
        if (asset.file) {
            envVars += `${I(3)}- AAS_MODEL_NAME=${asset.file.name}\n`;
        }

        // If the user typed a manual AAS ID / path, add AAS_ID
        if (asset.path && !asset.file) {
            envVars += `${I(3)}- AAS_ID=${asset.path}\n`;
        }

        // If user uploaded a file AND typed a path (AAS ID), include both
        if (asset.file && asset.path && asset.path !== asset.file.name) {
            envVars += `${I(3)}- AAS_ID=${asset.path}\n`;
        }

        envVars += `${I(3)}- AGENT_ID=${serviceName}@${xmppDomain}\n`;
        envVars += `${I(3)}- AGENT_PSSWD=${asset.password}\n`;

        // SMIA-I KB registration: only when both KB and ISM are enabled
        if (kbRegistrationEnabled) {
            envVars += `${I(3)}- SMIAI_KB_REGISTRATION=TRUE\n`;
        }

        let yaml =
            `${I(1)}${'smia-' + serviceName}:\n` +
            `${I(2)}image: ${dockerImage}\n` +
            `${I(2)}container_name: ${'smia-' + serviceName}\n` +
            `${I(2)}environment:\n` +
            envVars +
            `${I(2)}volumes:\n` +
            `${I(3)}- ./aas:/smia_archive/config/aas\n`;

        // Add depends_on block for XMPP server and/or SMIA ISM
        if (xmppNew || ismEnabled) {
            yaml += `${I(2)}depends_on:\n`;
            if (xmppNew) {
                yaml +=
                    `${I(3)}xmpp-server:\n` +
                    `${I(4)}condition: service_healthy\n`;
            }
            if (ismEnabled) {
                yaml +=
                    `${I(3)}smia-ism:\n` +
                    `${I(4)}condition: service_healthy\n`;
            }
        }

        return yaml;
    },

    /**
     * Injects extra_hosts into a service block string.
     * Adds `extra_hosts:\n  - "<domain>:<ip>"` after the first line (service name).
     */
    _injectExtraHosts: function (serviceBlock, I, domain, ip) {
        const lines = serviceBlock.split('\n');
        // Insert extra_hosts right after the service name line
        const extraHostsBlock =
            `${I(2)}extra_hosts:\n` +
            `${I(3)}- "${domain}:${ip}"`;
        // Find the service name line (first line) and insert after it
        lines.splice(1, 0, extraHostsBlock);
        return lines.join('\n');
    },

    // ── BaSyx configuration file builders ────────────────────────

    _buildBasyxAasEnvProperties: function () {
        return [
            '# BaSyx AAS Environment configuration',
            '# Generated by SMIA Environment Builder',
            'server.port=8081',
            'basyx.backend=MongoDB',
            'spring.mongodb.host=mongo',
            'spring.mongodb.port=27017',
            'spring.mongodb.database=aas-env',
            'spring.mongodb.authentication-database=admin',
            'spring.mongodb.username=mongoAdmin',
            'spring.mongodb.password=mongoPassword',
            'basyx.aasrepository.feature.registryintegration=http://aas-registry:8080',
            'basyx.submodelrepository.feature.registryintegration=http://sm-registry:8080',
            'basyx.cors.allowed-origins=*',
            'basyx.cors.allowed-methods=GET,POST,PATCH,DELETE,PUT,OPTIONS,HEAD',
        ].join('\n');
    },

    _buildBasyxAasRegistryYml: function () {
        return [
            '# BaSyx AAS Registry configuration',
            '# Generated by SMIA Environment Builder',
            'spring:',
            '  mongodb:',
            '    host: mongo',
            '    port: 27017',
            '    database: aas-registry',
            '    authentication-database: admin',
            '    username: mongoAdmin',
            '    password: mongoPassword',
        ].join('\n');
    },

    _buildBasyxSmRegistryYml: function () {
        return [
            '# BaSyx Submodel Registry configuration',
            '# Generated by SMIA Environment Builder',
            'spring:',
            '  mongodb:',
            '    host: mongo',
            '    port: 27017',
            '    database: sm-registry',
            '    authentication-database: admin',
            '    username: mongoAdmin',
            '    password: mongoPassword',
        ].join('\n');
    },

    /**
     * Builds the basyx-infra.yml file for the BaSyx Go variant.
     * Points all repositories/registries to the unified aas-environment (port 8082).
     * The aas-ui service mounts it from ./basyx/basyx-infra.yml.
     */
    _buildBasyxGoInfraYml: function () {
        return [
            '# BaSyx Go infrastructure endpoints',
            '# Generated by SMIA Environment Builder',
            'infrastructures:',
            '  default: infra1',
            '  infra1:',
            '    name: Minimal BaSyx',
            '    components:',
            '      aasDiscovery:',
            '        baseUrl: http://localhost:8082/lookup/shells',
            '      aasRegistry:',
            '        baseUrl: http://localhost:8082/shell-descriptors',
            '        hasDiscoveryIntegration: true',
            '      submodelRegistry:',
            '        baseUrl: http://localhost:8082/submodel-descriptors',
            '      aasRepository:',
            '        baseUrl: http://localhost:8082/shells',
            '        hasRegistryIntegration: true',
            '      submodelRepository:',
            '        baseUrl: http://localhost:8082/submodels',
            '        hasRegistryIntegration: true',
            '      conceptDescriptionRepository:',
            '        baseUrl: http://localhost:8082/concept-descriptions',
            '    security:',
            '      type: none',
        ].join('\n');
    },

    /**
     * Builds README.md for container (Docker Compose / K8s) mode.
     */
    _buildContainerReadme: function (s) {
        const envLabel = s.envType === 'docker' ? 'Docker Compose' : 'Kubernetes';
        let md = `# SMIA Environment - Generated Configuration\n\n`;
        md += `> Generated by **SMIA Environment Builder**\n\n`;
        md += `## Deployment Type: ${envLabel}\n\n`;

        // Configuration summary table
        md += `## Configuration Summary\n\n`;
        md += `| Setting | Value |\n|---|---|\n`;
        md += `| Environment | ${envLabel} |\n`;
        md += `| XMPP Server | ${s.xmpp.strategy === 'new' ? 'Ejabberd (new container)' : 'Existing (' + s.xmpp.domain + ')'} |\n`;
        if (s.xmpp.strategy === 'existing') {
            md += `| XMPP Domain | \`${s.xmpp.domain}\` |\n`;
            md += `| XMPP IP | \`${s.xmpp.ip}\` |\n`;
        }
        md += `| AAS Server | ${s.core.aasServer.type === 'basyx' ? `BaSyx (${(s.core.aasServer.basyxVariant || 'go') === 'go' ? 'Go' : 'Java'})` : s.core.aasServer.type === 'external' ? 'External' : 'None'} |\n`;
        md += `| SMIA-I KB | ${s.core.smiakb ? 'Enabled' : 'Disabled'} |\n`;
        md += `| SMIA ISM | ${s.core.ism ? 'Enabled' : 'Disabled'} |\n`;
        if (s.plan.hasPlan) md += `| Manufacturing Plan | Included |\n`;
        md += `| Assets | ${s.assets.length} |\n`;
        md += `| SMIA Operator | ${s.operator ? 'Enabled' : 'Disabled'} |\n`;
        md += `| Assets Simulator | ${s.assetsSimulator.enabled ? 'Enabled' : 'Disabled'} |\n`;

        // Running instructions — different for Docker vs Kubernetes
        md += `\n## How to Run\n\n`;
        if (s.envType === 'k8s') {
            // Kubernetes-specific instructions referencing deploy.sh
            md += `### Kubernetes (NFS + subPath + readOnly)\n\n`;
            md += `This deployment uses an NFS-backed PersistentVolumeClaim to share AAS model files with all SMIA pods.\n\n`;
            md += `#### Quick Start\n\n`;
            md += `Run the included deployment script (requires \`sudo\` for NFS setup):\n\n`;
            md += `\`\`\`bash\nchmod +x deploy.sh\n./deploy.sh\n\`\`\`\n\n`;
            md += `#### Manual Steps\n\n`;
            md += `If you prefer to deploy manually:\n\n`;
            md += `1. Set up an NFS server exporting the \`aas/\` directory.\n`;
            md += `2. Create the PersistentVolume and PersistentVolumeClaim (\`nfs-aas-pvc\`).\n`;
            md += `3. Apply the Kubernetes manifests:\n\n`;
            md += `\`\`\`bash\nkubectl apply -f kubernetes/\n\`\`\`\n\n`;
        } else {
            md += `### Docker Compose\n\n`;
            md += `\`\`\`bash\ndocker compose up -d\n\`\`\`\n\n`;
        }

        // Directory structure — different for Docker vs Kubernetes
        md += `## Directory Structure\n\n\`\`\`\n`;
        if (s.envType === 'k8s') {
            md += `deploy.sh                ← Automated NFS + K8s deployment script\n`;
            md += `kubernetes/              ← Kubernetes Deployment manifests\n`;
            s.assets.forEach((_, i) => {
                md += `  deploy-smia-${i + 1}.yaml\n`;
            });
        } else {
            md += `docker-compose.yml\n`;
        }
        md += `README.md\n`;
        md += `aas/                     ← AAS model files\n`;
        if (s.envType === 'docker' && s.xmpp.strategy === 'new') md += `xmpp_server/\n  ejabberd.yml           ← Ejabberd configuration\n`;
        if (s.envType === 'docker' && s.core.aasServer.type === 'basyx') {
            md += (s.core.aasServer.basyxVariant || 'go') === 'go'
                ? `basyx/                   ← BaSyx Go configuration files\n  rsa-key.pem\n  basyx-infra.yml\n`
                : `basyx/                   ← BaSyx configuration files\n  aas-env.properties\n  aas-registry.yml\n  sm-registry.yml\n`;
        }
        md += `\`\`\`\n`;

        md += `\n## Resources\n\n`;
        md += `- [SMIA GitHub Repository](https://github.com/ekhurtado/SMIA)\n`;
        md += `- [SMIA Documentation (Read the Docs)](https://smia.readthedocs.io)\n`;
        return md;
    },

    // ============================================================
    // ASSET UI MANAGEMENT
    // ============================================================

    addAssetUI: function () {
        const isLocal = (this.state.envType === 'local');
        if (isLocal && document.getElementById('assets-list').children.length > 0) return;

        const id = Date.now();
        const container = document.getElementById('assets-list');
        const div = document.createElement('div');
        div.className = 'asset-card';
        div.id = `asset-${id}`;

        const trashSvg = `<svg viewBox="0 0 24 24"><path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/></svg>`;

        div.innerHTML = `
            <div class="asset-header">
                <strong>New Asset Instance</strong>
                <button class="btn-icon-danger" onclick="SMIA_Builder.removeAsset('asset-${id}')" title="Remove Asset">
                    ${trashSvg}
                </button>
            </div>

            <div class="form-group">
                <label>AAS Model Source</label>
                <div class="file-upload-wrapper">
                    <input type="file" class="asset-file-input file-upload-input" accept=".aasx"
                           onchange="SMIA_Builder.handleFileSelect(this)">
                    <div class="file-upload-label">
                        <span class="file-text">Upload AASX File</span>
                        <span class="upload-icon">${ICONS.zipFile}</span>
                    </div>
                </div>
                <input type="text" class="asset-id-input smia-input"
                       placeholder="Or enter AAS ID manually" style="margin-top:10px;">
            </div>

            <div class="form-group" style="display: flex; gap: 1rem; margin-top: 10px;">
                <div style="flex: 1;">
                    <label>Agent JID</label>
                    <input type="text" class="agent-jid-input smia-input" placeholder="e.g., smia-1">
                </div>
                <div style="flex: 1;">
                    <label>Agent Password</label>
                    <input type="text" class="asset-password-input smia-input" placeholder="e.g., gcis1234">
                </div>
            </div>

            <div class="form-group">
                <label class="modern-checkbox">
                    <input type="checkbox" class="chk-extended">
                    <span class="checkmark"></span>
                    Extended SMIA (Custom Docker Image)
                </label>
                <input type="text" class="asset-image-input smia-input"
                       style="display:none; margin-top:5px;"
                       placeholder="Docker Image Name (e.g., my-repo/asset:v1)">
            </div>
        `;

        div.querySelector('.chk-extended').addEventListener('change', function (e) {
            div.querySelector('.asset-image-input').style.display = e.target.checked ? 'block' : 'none';
        });

        container.appendChild(div);

        if (isLocal) {
            document.getElementById('btn-add-asset').style.display = 'none';
        }
    },

    removeAsset: function (assetId) {
        const el = document.getElementById(assetId);
        if (el) el.remove();

        if (this.state.envType === 'local' &&
            document.getElementById('assets-list').children.length === 0) {
            const addBtn = document.getElementById('btn-add-asset');
            addBtn.textContent = '+ Add Asset (Optional)';
            addBtn.style.display = 'block';
        }
    },

    handleFileSelect: function (inputElement) {
        const label = inputElement.nextElementSibling;
        const textSpan = label.querySelector('.file-text');
        if (inputElement.files && inputElement.files.length > 0) {
            textSpan.textContent = inputElement.files[0].name;
            label.classList.add('has-file');
        } else {
            textSpan.textContent = 'Upload AASX File';
            label.classList.remove('has-file');
        }
    },

    // ============================================================
    // ASSETS SIMULATOR BUILDERS
    // ============================================================

    /**
     * Generates a Docker Compose service block for the Assets Simulator HTTP.
     * Uses image ekhurtado/smia-tools:latest-assets-simulator-http.
     *
     * @param {Function} I - Indentation helper
     * @param {object} s  - SMIA_Builder.state
     * @returns {string} Service YAML block
     */
    _yamlAssetsSimulator: function (I, s) {
        let yaml =
            `${I(1)}smia-assets-simulator-http:\n` +
            `${I(2)}image: ekhurtado/smia-tools:latest-assets-simulator-http\n` +
            `${I(2)}container_name: smia-assets-simulator-http\n` +
            `${I(2)}ports:\n` +
            `${I(3)}- "5000:5000"\n` +
            `${I(2)}environment:\n` +
            `${I(3)}- PRODUCTION_ASSETS=${s.assetsSimulator.productionAssets}\n` +
            `${I(3)}- MOBILE_ASSETS=${s.assetsSimulator.mobileAssets}\n` +
            `${I(3)}- HUMAN_ASSETS=${s.assetsSimulator.humanAssets}\n`;
        return yaml;
    },

    /**
     * Generates a Kubernetes Deployment YAML for the Assets Simulator HTTP.
     * Uses image ekhurtado/smia-tools:latest-assets-simulator-http.
     *
     * @param {object} s - SMIA_Builder.state
     * @returns {string} Deployment YAML
     */
    _yamlK8sAssetsSimulator: function (s) {
        return `apiVersion: apps/v1
kind: Deployment
metadata:
  name: assets-simulator-http
  labels:
    app: assets-simulator-http
spec:
  replicas: 1
  selector:
    matchLabels:
      app: assets-simulator-http
  template:
    metadata:
      labels:
        app: assets-simulator-http
    spec:
      containers:
        - name: assets-simulator-http
          image: ekhurtado/smia-tools:latest-assets-simulator-http
          ports:
            - containerPort: 5000
          env:
            - name: PRODUCTION_ASSETS
              value: "${s.assetsSimulator.productionAssets}"
            - name: MOBILE_ASSETS
              value: "${s.assetsSimulator.mobileAssets}"
            - name: HUMAN_ASSETS
              value: "${s.assetsSimulator.humanAssets}"
`;
    },

    /**
     * Generates a Kubernetes Service YAML (NodePort) to expose Assets Simulator HTTP.
     * Maps port 5000 → targetPort 5000, exposed on nodePort 31500.
     *
     * @returns {string} Service YAML
     */
    _yamlK8sAssetsSimulatorService: function () {
        return `apiVersion: v1
kind: Service
metadata:
  name: assets-simulator-http
spec:
  type: NodePort
  selector:
    app: assets-simulator-http
  ports:
    - name: "5000"
      port: 5000
      targetPort: 5000
      nodePort: 31500
`;
    },

    /**
     * Fetches the Assets Simulator HTTP subfolder from the main repository
     * and adds its contents to the output ZIP under `assets_simulator_http/`,
     * preserving the internal directory structure.
     *
     * Uses the same GitHub Trees API approach as _addOperatorToZip.
     *
     * @param {JSZip} zip
     * @param {object} s
     */
    _addAssetsSimulatorToZip: async function (zip, s) {
        const targetFolder = zip.folder('assets_simulator_http');
        const prefix = GITHUB_URLS.ASSETS_SIMULATOR_SUBFOLDER + '/';

        // ── Stage 1: Fetch the full repo tree and filter to the simulator subfolder ──
        let simulatorItems;
        try {
            const treeResp = await fetch(GITHUB_URLS.GITHUB_TREE);
            if (!treeResp.ok) throw new Error(`GitHub Trees API returned HTTP ${treeResp.status}`);

            const treeData = await treeResp.json();
            if (!treeData.tree || !Array.isArray(treeData.tree)) {
                throw new Error('Unexpected response format from GitHub Trees API');
            }

            if (treeData.truncated) {
                console.warn('[SMIA Builder] GitHub Trees API response was truncated. Some simulator files may be missing.');
            }

            // Keep only file blobs whose path is inside the simulator subfolder
            // Exclude .idea/ and other IDE configuration directories
            simulatorItems = treeData.tree.filter(item =>
                item.type === 'blob' &&
                item.path.startsWith(prefix) &&
                !item.path.includes('/.idea/')
            );

            if (simulatorItems.length === 0) {
                throw new Error(`No files found under "${GITHUB_URLS.ASSETS_SIMULATOR_SUBFOLDER}" in the repository tree.`);
            }
        } catch (err) {
            console.warn('[SMIA Builder] Could not fetch assets simulator file tree:', err);
            targetFolder.file('README.md',
                `# Assets Simulator HTTP\n\n` +
                `> ⚠️ Files could not be downloaded automatically.\n\n` +
                `**Reason:** ${err.message}\n\n` +
                `Please copy the contents of:\n` +
                `\`${GITHUB_URLS.ASSETS_SIMULATOR_SUBFOLDER}/\`\n` +
                `from the SMIA repository into this folder.\n`
            );
            return;
        }

        // ── Stage 2: Fetch each file in parallel, strip the subfolder prefix ──
        let successCount = 0;
        let failCount = 0;

        const fetchPromises = simulatorItems.map(item => {
            const rawUrl = `${GITHUB_URLS.OPERATOR_RAW_BASE}${item.path}`;
            // Strip the subfolder prefix so ZIP entry is relative
            const zipPath = item.path.slice(prefix.length);

            if (zipPath === 'main.py' || zipPath.endsWith('/main.py')) {
                return fetch(rawUrl)
                    .then(r => {
                        if (!r.ok) throw new Error(`HTTP ${r.status}`);
                        return r.text();
                    })
                    .then(text => {
                        const prodStr = JSON.stringify(s.assetsSimulator.productionAssets || '');
                        const mobStr = JSON.stringify(s.assetsSimulator.mobileAssets || '');
                        const humStr = JSON.stringify(s.assetsSimulator.humanAssets || '');

                        let modifiedText = text;
                        const targetLine = 'for a in [a.strip() for a in HUM_ASSETS_STR.split(",") if a.strip()]: ASSET_CATALOG[a] = "human"';
                        const addedLines = `${targetLine}\n\n` +
                            `# Activos anadidos desde SMIA Environment Builder (modo local)\n` +
                            `_extra_prod = ${prodStr}\n` +
                            `_extra_mob = ${mobStr}\n` +
                            `_extra_hum = ${humStr}\n` +
                            `for a in [a.strip() for a in _extra_prod.split(",") if a.strip()]: ASSET_CATALOG[a] = "robot"\n` +
                            `for a in [a.strip() for a in _extra_mob.split(",") if a.strip()]: ASSET_CATALOG[a] = "mobile"\n` +
                            `for a in [a.strip() for a in _extra_hum.split(",") if a.strip()]: ASSET_CATALOG[a] = "human"`;

                        modifiedText = modifiedText.replace(targetLine, addedLines);

                        targetFolder.file(zipPath, modifiedText);
                        successCount++;
                    })
                    .catch(err => {
                        console.warn(`[SMIA Builder] Failed to fetch string: ${item.path} — ${err.message}`);
                        failCount++;
                    });
            } else {
                return fetch(rawUrl)
                    .then(r => {
                        if (!r.ok) throw new Error(`HTTP ${r.status}`);
                        return r.arrayBuffer();
                    })
                    .then(data => {
                        targetFolder.file(zipPath, data);
                        successCount++;
                    })
                    .catch(err => {
                        console.warn(`[SMIA Builder] Failed to fetch: ${item.path} — ${err.message}`);
                        failCount++;
                    });
            }
        });

        await Promise.allSettled(fetchPromises);

        console.info(`[SMIA Builder] Assets Simulator: ${successCount} file(s) added, ${failCount} failed.`);

        if (successCount === 0) {
            targetFolder.file('README.md',
                `# Assets Simulator HTTP\n\n` +
                `> ⚠️ All ${failCount} file download(s) failed.\n\n` +
                `This is usually caused by a network restriction or GitHub rate limiting.\n\n` +
                `Please copy the contents of:\n` +
                `\`${GITHUB_URLS.ASSETS_SIMULATOR_SUBFOLDER}/\`\n` +
                `from the SMIA repository into this folder.\n`
            );
        }
    },
};