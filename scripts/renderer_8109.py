"""Reviewed renderer patches for ChatGPT 26.901.51231 (8109).

Kept separate from build 6396: 8109 splits the initial and primary bundles,
uses direct RPC calls, and has a different profile header. Every changed
anchor must occur exactly once. No vendor bundle is stored in this repository.
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def replace_once(text, before, after):
    count = text.count(before)
    if count != 1:
        raise RuntimeError(f'8109 anchor expected once, found {count}: {before[:100]}')
    return text.replace(before, after, 1)


def one(assets, pattern, anchor=None):
    paths = [p for p in assets.glob(pattern) if anchor is None or anchor in p.read_text()]
    if len(paths) != 1:
        raise RuntimeError(f'8109 expected one {pattern}, found {len(paths)}')
    return paths[0]


def function_text(text, name, next_name):
    start = text.index(f'function {name}(')
    end = text.index(f'function {next_name}(', start)
    return text[start:end]


def patch_renderer_8109(extracted, token):
    assets = extracted / 'webview/assets'
    index_path = extracted / 'webview/index.html'
    index_path.write_text(replace_once(index_path.read_text(), 'connect-src &#39;self&#39;',
                                     'connect-src &#39;self&#39; http://127.0.0.1:48123'))
    primary_path = one(assets, 'app-primary-*.js')
    primary = primary_path.read_text()
    component = (ROOT / 'ui/account-menu.js').read_text()
    bindings = {'e7':'cY', 'kXc':'ehn', 'QLs':'tq', 'Lo':'zx', 'Q':'qv',
                '_H':'xl', 'S2':'jq', 'BW':'QC', 'CH':'Sy', 'lt':'Ob', 'jLa':'gV'}
    component = re.sub(r'(?<![\w$])(' + '|'.join(map(re.escape, bindings)) + r')(?![\w$])',
                       lambda m: bindings[m[0]], component)
    component = component.replace('__CODEX_MUX_CONTROL_PORT__','48123').replace('__CODEX_MUX_CONTROL_TOKEN__',token)
    # These helpers are called by hooks in the initial bundle after primary loads.
    component += '\nObject.assign(globalThis,{codexMuxProfileData,codexMuxRateLimitResets,codexMuxConsumeRateLimitReset});\n'
    primary = replace_once(primary, 'function Ymn(e){', component + '\nfunction Ymn(e){')
    primary = replace_once(primary, 'usageItems:Dt,', 'usageItems:(0,cY.jsx)(CodexMuxAccountMenu,{}),')
    primary = replace_once(primary, 'children:[St,Mt,It,null,Lt,null,Rt,Bt,Dt,Vt]',
                           'children:[St,Mt,It,null,Lt,null,Rt,Bt,(0,cY.jsx)(CodexMuxAccountMenu,{}),Vt]')
    for anchor in ['triggerButton:jt,onOpenChange:c,children:[F,null]',
                   'open:s,onOpenChange:c,contentWidth:`panel`']:
        primary = replace_once(primary, anchor, anchor.replace('onOpenChange:c','onOpenChange:CodexMuxProfileMenuOpenChange(c)'))
    primary = replace_once(primary, 'function tq(e){', 'function tq(e){CodexMuxUseResetAccountState();')
    primary = replace_once(primary, 'let y=v;if(g!=null){', 'let y=window.__codexMuxSelectedUsageWindows??v;if(g!=null){')
    primary = replace_once(primary,
        'let _e;t[46]===he?_e=t[47]:(_e=(0,eq.jsxs)(mw,{children:[he,ge]}),t[46]=he,t[47]=_e);',
        'let _e=(0,eq.jsxs)(mw,{children:[he,ge,window.__codexMuxResetAccountSelector??null]});')
    for message in ['You’re out of Codex and Work usage','You’ve used all Codex and Work usage','You’ve reached your usage limit']:
        primary = replace_once(primary, f'defaultMessage:`{message}`', 'defaultMessage:`All connected subscriptions are depleted`')
    primary_path.write_text(primary)

    initial_path = one(assets, 'app-initial-*.js')
    initial = initial_path.read_text()
    # This build calls RPCs directly; scope at the request-client boundary, not
    # the obsolete list-apps UI message bridge. The mux removes the extra key.
    initial = replace_once(initial,
        'async sendRequest(e,t,n){return this.assertActive(),this.requestClient.sendRequest(e,t,n)}',
        'async sendRequest(e,t,n){let a=globalThis.__codexMuxPluginAccountId;'
        'if(a&&[`app/list`,`app/installed`,`app/read`,`mcpServerStatus/list`,`mcpServer/oauth/login`].includes(e))'
        't={...(t??{}),codexMuxAccountId:a};return this.assertActive(),this.requestClient.sendRequest(e,t,n)}')
    # Include the account in the MCP request deduplication key too.
    initial = replace_once(initial,
        'listMcpServers(e,t){let n=JSON.stringify({options:t,params:e})',
        'listMcpServers(e,t){let a=globalThis.__codexMuxPluginAccountId;'
        'if(a)e={...(e??{}),codexMuxAccountId:a};let n=JSON.stringify({options:t,params:e})')
    initial = replace_once(initial, 'let e=await _O.safeGet(`/wham/profiles/me`)',
                           'let e=await globalThis.codexMuxProfileData(globalThis.__codexMuxSelectedProfileAccountId??null)')
    initial = replace_once(initial, function_text(initial, 'v2i', 'y2i'),
        'function v2i(){WR();Cb(null);let a=window.__codexMuxResetAccountId;return Mb({'
        'queryKey:[`rate-limit-reset-credits`,a??`primary`],queryFn:a?()=>globalThis.codexMuxRateLimitResets(a):b2i,'
        'select:y2i,refetchInterval:lD.ONE_MINUTE,staleTime:lD.FIVE_SECONDS})}')
    initial = replace_once(initial, function_text(initial, 'x2i', 'S2i'),
        'function x2i(){let e=Ob(),t=sD(),a=window.__codexMuxResetAccountId,'
        'r=[`rate-limit-reset-credits`,a??`primary`];return Fb({'
        'mutationFn:a?i=>globalThis.codexMuxConsumeRateLimitReset(a,i):S2i,'
        'onSuccess:(n,i)=>{let o=n.code;if(o===`reset`||o===`already_redeemed`){'
        'let c=o===`reset`?n.credit?.id??i.creditId:i.creditId;e.setQueryData(r,v=>i0i(v,o,c))}'
        'Promise.all([t([`rate-limit-status`]),t([`rate-limit-reset-credits`])])}})}')
    initial_path.write_text(initial)

    plugins_path = one(assets, 'plugins-settings-*.js', 'action:F,children:w})')
    plugins_path.write_text(replace_once(plugins_path.read_text(), 'action:F,children:w})',
        'action:F,children:[globalThis.CodexMuxPluginScope?.()??null,w]})'))
    patch_profile(assets)
    patch_thread(assets, token)


def patch_profile(assets):
    path = one(assets, 'profile-*.js', 'function ta(e){')
    bundle = path.read_text()
    # Put the account selector above the redesigned editable profile header.
    # Hide the primary-account editing UI while showing combined/secondary data.
    anchor = 'avatar:(0,$.jsxs)($.Fragment,{children:['
    bundle = replace_once(bundle, anchor,
        'avatar:(0,$.jsxs)($.Fragment,{children:[globalThis.CodexMuxProfileAvatarStack?.({onSelect:()=>M.refetch()})??null,')
    bundle = replace_once(bundle, '`group relative flex size-20 rounded-full outline-none focus-within:ring-1 focus-within:ring-ring`',
        '`hidden`')
    bundle = replace_once(bundle, '(0,$.jsx)(re,{account:Qe==null?', '(0,$.jsx)(CodexMuxProfileHeader,{account:Qe==null?')
    bundle += '\nfunction CodexMuxProfileHeader(props){let id=globalThis.__codexMuxSelectedProfileAccountId;'
    bundle += 'let account=(globalThis.__codexMuxCombinedProfileAccounts??[]).find(a=>a.id===id);'
    bundle += 'return(0,$.jsx)(re,{...props,account:account?.planLabel??null,'
    bundle += 'displayName:id?props.displayName:`Combined subscriptions`,username:id?props.username:null})}\n'
    bundle = replace_once(bundle, '_t=()=>{G(i,je,{action:tt.CODEX_PROFILE_EDIT_ACTION_OPENED}),we(!0)}',
        '_t=()=>{if(globalThis.__codexMuxSelectedProfileAccountId!==`primary`){'
        'window.alert(`Select Primary before editing your profile.`);return}'
        'G(i,je,{action:tt.CODEX_PROFILE_EDIT_ACTION_OPENED}),we(!0)}')
    path.write_text(bundle)


def patch_thread(assets, token):
    path = one(assets, 'local-conversation-thread-*.js', 'sectionKey:`tool-sources`')
    bundle = path.read_text()
    component = (ROOT / 'ui/thread-subscription.js').read_text()
    bindings = {'$n':'Fo', 'sr':'Mr', 'TE':'ob', 'zE':'sb', 'K':'Z'}
    component = re.sub(r'(?<![\w$])(' + '|'.join(map(re.escape, bindings)) + r')(?![\w$])',
                       lambda m: bindings[m[0]], component)
    component = component.replace('__CODEX_MUX_CONTROL_PORT__','48123').replace('__CODEX_MUX_CONTROL_TOKEN__',token)
    # Render alongside the existing artifact section, which is part of summary.
    # This function's own module initializes the React and JSX bindings above.
    anchor = 'if(o===`list`)return H;'
    bundle = replace_once(bundle, anchor, anchor + 'H=(0,sb.jsxs)(sb.Fragment,{children:[(0,sb.jsx)(CodexMuxThreadSubscription,{}),H]});')
    bundle += '\n' + component
    path.write_text(bundle)
