import { Box, Container, Typography } from "@mui/material";
import HorizonAppBar from "../../components/HorizonAppBar";
import { useEffect, useState } from "react";
import { Auth } from "aws-amplify";

const initialState = {
    user: undefined,
    isLoggedIn: false,
    loading: true
};

function TermsAndConditionsPage() {
    const [state, setState] = useState(initialState);
    useEffect(() => {
        async function checkUser() {
            await Auth.currentAuthenticatedUser({
                bypassCache: false
            }).then(user => {
                setState({
                    ...initialState,
                    user: user,
                    isLoggedIn: true,
                    loading: false
                });
                console.log(user)
            }).catch(err => {
                console.log(err);
                setState({
                    ...initialState,
                    user: undefined,
                    isLoggedIn: false,
                    loading: false
                });
            });
        }
        checkUser();
    }, []);

    const signOut = async () => {
        try {
            await Auth.signOut({ global: true });
            setState({ ...initialState, loading: false });
        } catch (error) {
            console.log('error signing out: ', error);
        }
    }

    if (state.loading) {
        return (<div className="main-box">
            <HorizonAppBar />
            <p>Loading...</p>
        </div>)
    }
    return (
        <Box>
            <HorizonAppBar user={state.user} signOut={signOut} />
            <Box component="main" sx={{ flexGrow: 1, mt: 3 }}>
                <Container maxWidth="xl">
                    <Typography variant="h4" align="left" sx={{ mb: 3, fontWeight: 700 }} >
                        Horizon AI Terms and Conditions
                    </Typography>
                    <Typography variant="body1" sx={{ mb: 2 }}>
                        These Terms govern<br />
                        - the use of Horizon AI, and,<br />
                        - any other related Agreement or legal relationship with the Owner in a legally binding way. Capitalized words are defined in the relevant dedicated section of this documen<br />
                        The User must read this document carefully.<br />
                        Horizon AI is provided by:<br />
                        Please email the company for details.<br />
                        Owner contact email: team@gethorizon.ai
                    </Typography>
                    <Typography variant="h5" align="left" sx={{ mb: 3, fontWeight: 700 }} >
                        What the User should know at a glance
                    </Typography>
                    <Typography variant="body1" sx={{ mb: 2 }}>
                        Please note that some provisions in these Terms may only apply to certain categories of Users. In particular, certain provisions may only apply to Consumers or to those Users that do not qualify as Consumers. Such limitations are always explicitly mentioned within each affected clause. In the absence of any such mention, clauses apply to all Users.
                    </Typography>
                    <Typography variant="h5" align="left" sx={{ mb: 3, fontWeight: 700 }} >
                        TERMS OF USE
                    </Typography>
                    <Typography variant="body1" sx={{ mb: 2 }}>
                        Unless otherwise specified, the terms of use detailed in this section apply generally when using Horizon AI.<br />
                        Single or additional conditions of use or access may apply in specific scenarios and in such cases are additionally indicated within this document.<br />
                        By using Horizon AI, Users confirm to meet the following requirements:<br />
                        - User will use the service as recommended and designed by Horizon AI<br />
                        - User will not attempt to resell Horizon AI, without gaining explicit permission from Horizon AI<br />
                        - User will not misuse or utilize the service in any way, especially to conduct any unlawful activity<br />
                    </Typography>
                    <Typography variant="h5" align="left" sx={{ mb: 3, fontWeight: 700 }} >
                        Content on Horizon AI
                    </Typography>
                    <Typography variant="body1" sx={{ mb: 2 }}>
                        Unless where otherwise specified or clearly recognizable, all content and services (i.e., material) available on Horizon AI is owned or provided by the Owner or its licensors.<br />
                        The Owner undertakes its utmost effort to ensure that the material provided on Horizon AI infringes no applicable legal provisions or third-party rights. However, it may not always be possible to achieve such a result.<br />
                        In such cases, without prejudice to any legal prerogatives of Users to enforce their rights, Users are kindly asked to preferably report related complaints using the contact details provided in this document.
                    </Typography>
                    <Typography variant="h6" align="left" sx={{ mb: 3, fontWeight: 700 }} >
                        Rights regarding content on Horizon AI - All rights reserved
                    </Typography>
                    <Typography variant="body1" sx={{ mb: 2 }}>
                        The Owner holds and reserves all intellectual property rights for any such content.<br />
                        Users may not therefore use such content in any way that is not necessary or implicit in the proper use of the Service.<br />
                        In particular, but without limitation, Users may not copy, download, share (beyond the limits set forth below), modify, translate, transform, publish, transmit, sell, sublicense, edit, transfer/assign to third parties or create derivative works from the content available on Horizon AI, nor allow any third party to do so through the User or their device, even without the User's knowledge.<br />
                        Where explicitly stated on Horizon AI, the User may download, copy and/or share some content available through Horizon AI for its sole personal and non-commercial use and provided that the copyright attributions and all the other attributions requested by the Owner are correctly implemented.<br />
                        Any applicable statutory limitation or exception to copyright shall stay unaffected.
                    </Typography>
                    <Typography variant="h5" align="left" sx={{ mb: 3, fontWeight: 700 }} >
                        Access to external resources
                    </Typography>
                    <Typography variant="body1" sx={{ mb: 2 }}>
                        Through Horizon AI Users may have access to external resources provided by third parties. Users acknowledge and accept that the Owner has no control over such resources and is therefore not responsible for their content and availability.<br />
                        Conditions applicable to any resources provided by third parties, including those applicable to any possible grant of rights in content, result from each such third parties' terms and conditions or, in the absence of those, applicable statutory law.
                    </Typography>
                    <Typography variant="h5" align="left" sx={{ mb: 3, fontWeight: 700 }} >
                        Acceptable use
                    </Typography>
                    <Typography variant="body1" sx={{ mb: 2 }}>
                        Horizon AI and the Service may only be used within the scope of what they are provided for, under these Terms and applicable law.<br />
                        Users are solely responsible for making sure that their use of Horizon AI and/or the Service violates no applicable law, regulations or third-party rights.<br />
                        Therefore, the Owner reserves the right to take any appropriate measure to protect its legitimate interests including by denying Users access to Horizon AI or the Service, terminating contracts, reporting any misconduct performed through Horizon AI or the Service to the competent authorities - such as judicial or administrative authorities - whenever Users engage or are suspected to engage in any of the following activities:<br />
                        - violate laws, regulations and/or these Terms;<br />
                        - infringe any third-party rights;<br />
                        - considerably impair the Owner's legitimate interests;<br />
                        - offend the Owner or any third party.
                    </Typography>
                    <Typography variant="h5" align="left" sx={{ mb: 3, fontWeight: 700 }} >
                        Liability and indemnification
                    </Typography>
                    <Typography variant="h6" sx={{ mb: 2 }}>
                        Disclaimer
                    </Typography>
                    <Typography variant="body1" sx={{ mb: 2 }}>
                        Except as set forth in this section, Horizon AI makes no warranties, express or implied, statutory or otherwise, including, but not limited to, warranties of merchantability, title, fitness for a particular purpose, or non infringement. Horizon AI will not be liable for delays, interruptions, service failures or other problems inherent in the use of the internet and electronic communications or other systems.
                    </Typography>
                    <Typography variant="h5" align="left" sx={{ mb: 3, fontWeight: 700 }} >
                        US Users
                    </Typography>
                    <Typography variant="h6" sx={{ mb: 2 }}>
                        Disclaimer of Warranties
                    </Typography>
                    <Typography variant="body1" sx={{ mb: 2 }}>
                        Horizon AI is provided strictly on an “as is” and “as available” basis. Use of the Service is at Users' own risk. To the maximum extent permitted by applicable law, the Owner expressly disclaims all conditions, representations, and warranties — whether express, implied, statutory or otherwise, including, but not limited to, any implied warranty of merchantability, fitness for a particular purpose, or non-infringement of third-party rights. No advice or information, whether oral or written, obtained by user from owner or through the Service will create any warranty not expressly stated herein.<br />
                        Without limiting the foregoing, the Owner, its subsidiaries, affiliates, licensors, officers, directors, agents, co-branders, partners, suppliers and employees do not warrant that the content is accurate, reliable or correct; that the Service will meet Users' requirements; that the Service will be available at any particular time or location, uninterrupted or secure; that any defects or errors will be corrected; or that the Service is free of viruses or other harmful components. Any content downloaded or otherwise obtained through the use of the Service is downloaded at users own risk and users shall be solely responsible for any damage to Users' computer system or mobile device or loss of data that results from such download or Users' use of the Service.<br />
                        The Owner does not warrant, endorse, guarantee, or assume responsibility for any product or service advertised or offered by a third party through the Service or any hyperlinked website or service, and the Owner shall not be a party to or in any way monitor any transaction between Users and third-party providers of products or services.<br />
                        The Service may become inaccessible or it may not function properly with Users' web browser, mobile device, and/or operating system. The owner cannot be held liable for any perceived or actual damages arising from Service content, operation, or use of this Service.
                        Federal law, some states, and other jurisdictions, do not allow the exclusion and limitations of certain implied warranties. The above exclusions may not apply to Users. This Agreement gives Users specific legal rights, and Users may also have other rights which vary from state to state. The disclaimers and exclusions under this agreement shall not apply to the extent prohibited by applicable law.
                    </Typography>
                    <Typography variant="h6" sx={{ mb: 2 }}>
                        Limitations of liability
                    </Typography>
                    <Typography variant="body1" sx={{ mb: 2 }}>
                        To the maximum extent permitted by applicable law, in no event shall the Owner, and its subsidiaries, affiliates, officers, directors, agents, co-branders, partners, suppliers and employees be liable for<br />
                        - any indirect, punitive, incidental, special, consequential or exemplary damages, including without limitation damages for loss of profits, goodwill, use, data or other intangible losses, arising out of or relating to the use of, or inability to use, the Service; and<br />
                        - any damage, loss or injury resulting from hacking, tampering or other unauthorized access or use of the Service or User account or the information contained therein;
                        - any errors, mistakes, or inaccuracies of content;<br />
                        - personal injury or property damage, of any nature whatsoever, resulting from User access to or use of the Service;<br />
                        - any unauthorized access to or use of the Owner’s secure servers and/or any and all personal information stored therein;<br />
                        - any interruption or cessation of transmission to or from the Service;<br />
                        - any bugs, viruses, trojan horses, or the like that may be transmitted to or through the Service;<br />
                        - any errors or omissions in any content or for any loss or damage incurred as a result of the use of any content posted, emailed, transmitted, or otherwise made available through the Service; and/or<br />
                        - the defamatory, offensive, or illegal conduct of any User or third party. In no event shall the Owner, and its subsidiaries, affiliates, officers, directors, agents, co-branders, partners, suppliers and employees be liable for any claims, proceedings, liabilities, obligations, damages, losses or costs in an amount exceeding the amount paid by User to the Owner hereunder in the preceding 12 months, or the period of duration of this agreement between the Owner and User, whichever is shorter.<br />
                        This limitation of liability section shall apply to the fullest extent permitted by law in the applicable jurisdiction whether the alleged liability is based on contract, tort, negligence, strict liability, or any other basis, even if company has been advised of the possibility of such damage.<br />
                        Some jurisdictions do not allow the exclusion or limitation of incidental or consequential damages, therefore the above limitations or exclusions may not apply to User. The terms give User specific legal rights, and User may also have other rights which vary from jurisdiction to jurisdiction. The disclaimers, exclusions, and limitations of liability under the terms shall not apply to the extent prohibited by applicable law.
                    </Typography>
                    <Typography variant="h6" sx={{ mb: 2 }}>
                        Indemnification
                    </Typography>
                    <Typography variant="body1" sx={{ mb: 2 }}>
                        The User agrees to defend, indemnify and hold the Owner and its subsidiaries, affiliates, officers, directors, agents, co-branders, partners, suppliers and employees harmless from and against any and all claims or demands, damages, obligations, losses, liabilities, costs or debt, and expenses, including, but not limited to, legal fees and expenses, arising from<br />
                        - User's use of and access to the Service, including any data or content transmitted or received by User;<br />
                        - User's violation of these terms, including, but not limited to, User's breach of any of the representations and warranties set forth in these terms;<br />
                        - User's violation of any third-party rights, including, but not limited to, any right of privacy or intellectual property rights;<br />
                        - User's violation of any statutory law, rule, or regulation;<br />
                        - any content that is submitted from User's account, including third party access with User's unique username, password or other security measure, if applicable, including, but not limited to, misleading, false, or inaccurate information;<br />
                        - User's willful misconduct; or<br />
                        - statutory provision by User or its affiliates, officers, directors, agents, co-branders, partners, suppliers and employees to the extent allowed by applicable law.
                    </Typography>
                    <Typography variant="h5" sx={{ mb: 2 }}>
                        Australian Users
                    </Typography>
                    <Typography variant="h6" sx={{ mb: 2 }}>
                        Limitation of Liability
                    </Typography>
                    <Typography variant="body1" sx={{ mb: 2 }}>
                        Nothing in these Terms excludes, restricts or modifies any guarantee, condition, warranty, right or remedy which the User may have under the Competition and Consumer Act 2010 (Cth) or any similar State and Territory legislation and which cannot be excluded, restricted or modified (non-excludable right). To the fullest extent permitted by law, our liability to the User, including liability for a breach of a non-excludable right and liability which is not otherwise excluded under these Terms of Use, is limited, at the Owner's sole discretion, to the re-performance of the services or the payment of the cost of having the services supplied again.
                    </Typography>
                    <Typography variant="h5" sx={{ mb: 2 }}>
                        Common provisions
                    </Typography>
                    <Typography variant="h6" sx={{ mb: 2 }}>
                        No Waiver
                    </Typography>
                    <Typography variant="body1" sx={{ mb: 2 }}>
                        The Owner's failure to assert any right or provision under these Terms shall not constitute a waiver of any such right or provision. No waiver shall be considered a further or continuing waiver of such term or any other term.
                    </Typography>
                    <Typography variant="h6" sx={{ mb: 2 }}>
                        Service interruption
                    </Typography>
                    <Typography variant="body1" sx={{ mb: 2 }}>
                        To ensure the best possible service level, the Owner reserves the right to interrupt the Service for maintenance, system updates or any other changes, informing the Users appropriately.
                        Within the limits of law, the Owner may also decide to suspend or terminate the Service altogether. If the Service is terminated, the Owner will cooperate with Users to enable them to withdraw Personal Data or information in accordance with applicable law.<br />
                        Additionally, the Service might not be available due to reasons outside the Owner's reasonable control, such as “force majeure” (eg. labor actions, infrastructural breakdowns or blackouts etc).
                    </Typography>
                    <Typography variant="h6" sx={{ mb: 2 }}>
                        Service reselling
                    </Typography>
                    <Typography variant="body1" sx={{ mb: 2 }}>
                        Users may not reproduce, duplicate, copy, sell, resell or exploit any portion of Horizon AI and of its Service without the Owner's express prior written permission, granted either directly or through a legitimate reselling program.
                    </Typography>
                    <Typography variant="h6" sx={{ mb: 2 }}>
                        Intellectual property rights
                    </Typography>
                    <Typography variant="body1" sx={{ mb: 2 }}>
                        Without prejudice to any more specific provision of these Terms, any intellectual property rights, such as copyrights, trademark rights, patent rights and design rights related to Horizon AI are the exclusive property of the Owner or its licensors and are subject to the protection granted by applicable laws or international treaties relating to intellectual property.<br />
                        All trademarks — nominal or figurative — and all other marks, trade names, service marks, word marks, illustrations, images, or logos appearing in connection with Horizon AI are, and remain, the exclusive property of the Owner or its licensors and are subject to the protection granted by applicable laws or international treaties related to intellectual property.
                    </Typography>
                    <Typography variant="h6" sx={{ mb: 2 }}>
                        Changes to these Terms
                    </Typography>
                    <Typography variant="body1" sx={{ mb: 2 }}>
                        The Owner reserves the right to amend or otherwise modify these Terms at any time. In such cases, the Owner will appropriately inform the User of these changes.<br />
                        Such changes will only affect the relationship with the User for the future.<br />
                        The continued use of the Service will signify the User's acceptance of the revised Terms. If Users do not wish to be bound by the changes, they must stop using the Service. Failure to accept the revised Terms, may entitle either party to terminate the Agreement.<br />
                        The applicable previous version will govern the relationship prior to the User's acceptance. The User can obtain any previous version from the Owner.<br />
                        If required by applicable law, the Owner will specify the date by which the modified Terms will enter into force.
                    </Typography>
                    <Typography variant="h6" sx={{ mb: 2 }}>
                        Assignment of contract
                    </Typography>
                    <Typography variant="body1" sx={{ mb: 2 }}>
                        The Owner reserves the right to transfer, assign, dispose of by novation, or subcontract any or all rights or obligations under these Terms, taking the User's legitimate interests into account. Provisions regarding changes of these Terms will apply accordingly.<br />
                        Users may not assign or transfer their rights or obligations under these Terms in any way, without the written permission of the Owner.
                    </Typography>
                    <Typography variant="h6" sx={{ mb: 2 }}>
                        Contacts
                    </Typography>
                    <Typography variant="body1" sx={{ mb: 2 }}>
                        All communications relating to the use of Horizon AI must be sent using the contact information stated in this document.
                    </Typography>
                    <Typography variant="h6" sx={{ mb: 2 }}>
                        Severability
                    </Typography>
                    <Typography variant="body1" sx={{ mb: 2 }}>
                        Should any provision of these Terms be deemed or become invalid or unenforceable under applicable law, the invalidity or unenforceability of such provision shall not affect the validity of the remaining provisions, which shall remain in full force and effect.<br /><br />

                        EU Users<br />
                        Should any provision of these Terms be or be deemed void, invalid or unenforceable, the parties shall do their best to find, in an amicable way, an agreement on valid and enforceable provisions thereby substituting the void, invalid or unenforceable parts.<br />
                        In case of failure to do so, the void, invalid or unenforceable provisions shall be replaced by the applicable statutory provisions, if so permitted or stated under the applicable law.<br />
                        Without prejudice to the above, the nullity, invalidity or the impossibility to enforce a particular provision of these Terms shall not nullify the entire Agreement, unless the severed provisions are essential to the Agreement, or of such importance that the parties would not have entered into the contract if they had known that the provision would not be valid, or in cases where the remaining provisions would translate into an unacceptable hardship on any of the parties.<br /><br />

                        US Users<br />
                        Any such invalid or unenforceable provision will be interpreted, construed and reformed to the extent reasonably required to render it valid, enforceable and consistent with its original intent. These Terms constitute the entire Agreement between Users and the Owner with respect to the subject matter hereof, and supersede all other communications, including but not limited to all prior agreements, between the parties with respect to such subject matter. These Terms will be enforced to the fullest extent permitted by law.
                    </Typography>
                    <Typography variant="h5" sx={{ mb: 2 }}>
                        Governing law
                    </Typography>
                    <Typography variant="body1" sx={{ mb: 2 }}>
                        These Terms are governed by the law of the place where the Owner is based, as disclosed in the relevant section of this document, without regard to conflict of laws principles.
                    </Typography>
                    <Typography variant="h6" sx={{ mb: 2 }}>
                        Exception for European Consumers
                    </Typography>
                    <Typography variant="body1" sx={{ mb: 2 }}>
                        However, regardless of the above, if the User qualifies as a European Consumer and has their habitual residence in a country where the law provides for a higher consumer protection standard, such higher standards shall prevail.
                    </Typography>
                    <Typography variant="h5" sx={{ mb: 2 }}>
                        Venue of jurisdiction
                    </Typography>
                    <Typography variant="body1" sx={{ mb: 2 }}>
                        The exclusive competence to decide on any controversy resulting from or connected to these Terms lies with the courts of the place where the Owner is based, as displayed in the relevant section of this document.
                    </Typography>
                    <Typography variant="h6" sx={{ mb: 2 }}>
                        Exception for European Consumers
                    </Typography>
                    <Typography variant="body1" sx={{ mb: 2 }}>
                        The above does not apply to any Users that qualify as European Consumers, nor to Consumers based in Switzerland, Norway or Iceland.
                    </Typography>
                </Container>
            </Box>
        </Box >
    );
}

export default TermsAndConditionsPage
