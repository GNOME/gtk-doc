<?xml version='1.0'?> <!--*- mode: xml -*-->
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                version="1.0">

  <!-- import the chunked XSL stylesheet -->
  <xsl:import href="http://docbook.sourceforge.net/release/xsl/current/html/chunk.xsl"/>
  <xsl:include href="devhelp.xsl"/>
  <xsl:include href="version-greater-or-equal.xsl"/>

  <!-- change some parameters -->
  <xsl:param name="toc.section.depth">1</xsl:param>

  <xsl:param name="default.encoding" select="'ISO-8859-1'"/>
  <xsl:param name="chunk.fast" select="1"/> 
  <xsl:param name="chapter.autolabel" select="0"/>
  <xsl:param name="use.id.as.filename" select="'1'"/>
  <xsl:param name="html.ext" select="'.html'"/>
  <xsl:param name="refentry.generate.name" select="0"/>
  <xsl:param name="refentry.generate.title" select="1"/>
  <xsl:param name="index.on.role" select="1"/>

  <!-- display variablelists as tables -->
  <xsl:param name="variablelist.as.table" select="1"/>

  <!-- this gets set on the command line ... -->
  <xsl:param name="gtkdoc.version" select="''"/>
  <xsl:param name="gtkdoc.bookname" select="''"/>

  <!-- ========================================================= -->
  <!-- template to create the index.sgml anchor index -->

  <xsl:template match="book|article">
    <xsl:variable name="tooldver">
      <xsl:call-template name="version-greater-or-equal">
        <xsl:with-param name="ver1" select="$VERSION" />
        <xsl:with-param name="ver2">1.36</xsl:with-param>
      </xsl:call-template>
    </xsl:variable>
    <xsl:if test="$tooldver = 0">
      <xsl:message terminate="yes">
FATAL-ERROR: You need the DocBook XSL Stylesheets version 1.36 or higher
to build the documentation. 
Get a newer version at http://docbook.sourceforge.net/projects/xsl/
      </xsl:message>
    </xsl:if>
    <xsl:apply-imports/>

    <!-- generate the index.sgml href index -->
    <xsl:call-template name="generate.index"/>
    <xsl:call-template name="generate.devhelp"/>
  </xsl:template>

  <xsl:template name="generate.index">
    <xsl:call-template name="write.text.chunk">
      <xsl:with-param name="filename" select="'index.sgml'"/>
      <xsl:with-param name="content">
        <!-- check all anchor and refentry elements -->
        <xsl:apply-templates select="//anchor|//refentry"
                             mode="generate.index.mode"/>
      </xsl:with-param>
      <xsl:with-param name="encoding" select="'utf-8'"/>
    </xsl:call-template>
  </xsl:template>

  <xsl:template match="*" mode="generate.index.mode">
    <xsl:if test="not(@href)">
      <xsl:text>&lt;ANCHOR id=&quot;</xsl:text>
      <xsl:value-of select="@id"/>
      <xsl:text>&quot; href=&quot;</xsl:text>
      <xsl:if test="$gtkdoc.bookname">
        <xsl:value-of select="$gtkdoc.bookname"/>
        <xsl:text>/</xsl:text>
      </xsl:if>
      <xsl:call-template name="href.target"/>
      <xsl:text>&quot;&gt;
</xsl:text>
    </xsl:if>
  </xsl:template>

  <!-- ========================================================= -->
  <!-- template to output gtkdoclink elements for the unknown targets -->

  <xsl:template match="link">
    <xsl:choose>
      <xsl:when test="id(@linkend)">
        <xsl:apply-imports/>
      </xsl:when>
      <xsl:otherwise>
        <GTKDOCLINK HREF="{@linkend}">
          <xsl:apply-templates/>
        </GTKDOCLINK>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <!-- ========================================================= -->
  <!-- Below are the visual portions of the stylesheet.  They provide
       the normal gtk-doc output style. -->

  <xsl:param name="shade.verbatim" select="0"/>
  <xsl:param name="refentry.separator" select="0"/>

  <xsl:template match="refsect2">
    <xsl:if test="preceding-sibling::refsect2">
      <hr/>
    </xsl:if>
    <xsl:apply-imports/>
  </xsl:template>

  <xsl:template name="user.head.content">
    <xsl:if test="$gtkdoc.version">
      <meta name="generator"
            content="GTK-Doc V{$gtkdoc.version} (XML mode)"/>
    </xsl:if>
    <link rel="stylesheet" href="style.css" type="text/css"/>
  </xsl:template>

  <xsl:template match="title" mode="book.titlepage.recto.mode">
    <table class="navigation" width="100%"
           cellpadding="2" cellspacing="0">
      <tr>
        <th valign="middle">
          <p class="{name(.)}">
            <xsl:value-of select="."/>
          </p>
        </th>
      </tr>
    </table>
  </xsl:template>

  <xsl:template name="header.navigation">
    <xsl:param name="prev" select="/foo"/>
    <xsl:param name="next" select="/foo"/>
    <xsl:variable name="home" select="/*[1]"/>
    <xsl:variable name="up" select="parent::*"/>

    <xsl:if test="$suppress.navigation = '0' and $home != .">
      <table class="navigation" width="100%"
             summary = "Navigation header" cellpadding="2" cellspacing="2">
        <tr valign="middle">
          <xsl:if test="count($prev) > 0">
            <td>
              <a accesskey="p">
                <xsl:attribute name="href">
                  <xsl:call-template name="href.target">
                    <xsl:with-param name="object" select="$prev"/>
                  </xsl:call-template>
                </xsl:attribute>
                <img src="left.png" width="24" height="24" border="0">
                  <xsl:attribute name="alt">
                    <xsl:call-template name="gentext">
                      <xsl:with-param name="key">nav-prev</xsl:with-param>
                    </xsl:call-template>
                  </xsl:attribute>
                </img>
              </a>
            </td>
          </xsl:if>
          <xsl:if test="count($up) > 0 and $up != $home">
            <td>
              <a accesskey="u">
                <xsl:attribute name="href">
                  <xsl:call-template name="href.target">
                    <xsl:with-param name="object" select="$up"/>
                  </xsl:call-template>
                </xsl:attribute>
                <img src="up.png" width="24" height="24" border="0">
                  <xsl:attribute name="alt">
                    <xsl:call-template name="gentext">
                      <xsl:with-param name="key">nav-up</xsl:with-param>
                    </xsl:call-template>
                  </xsl:attribute>
                </img>
              </a>
            </td>
          </xsl:if>
          <xsl:if test="$home != .">
            <td>
              <a accesskey="h">
                <xsl:attribute name="href">
                  <xsl:call-template name="href.target">
                    <xsl:with-param name="object" select="$home"/>
                  </xsl:call-template>
                </xsl:attribute>
                <img src="home.png" width="24" height="24" border="0">
                  <xsl:attribute name="alt">
                    <xsl:call-template name="gentext">
                      <xsl:with-param name="key">nav-home</xsl:with-param>
                    </xsl:call-template>
                  </xsl:attribute>
                </img>
              </a>
            </td>
          </xsl:if>
          <th width="100%" align="center">
            <xsl:apply-templates select="$home"
                                 mode="object.title.markup"/>
          </th>
          <xsl:if test="count($next) > 0">
            <td>
              <a accesskey="n">
                <xsl:attribute name="href">
                  <xsl:call-template name="href.target">
                    <xsl:with-param name="object" select="$next"/>
                  </xsl:call-template>
                </xsl:attribute>
                <img src="right.png" width="24" height="24" border="0">
                  <xsl:attribute name="alt">
                    <xsl:call-template name="gentext">
                      <xsl:with-param name="key">nav-next</xsl:with-param>
                    </xsl:call-template>
                  </xsl:attribute>
                </img>
              </a>
            </td>
          </xsl:if>
        </tr>
      </table>
    </xsl:if>
  </xsl:template>

  <xsl:template name="footer.navigation">
    <xsl:param name="prev" select="/foo"/>
    <xsl:param name="next" select="/foo"/>

    <xsl:if test="$suppress.navigation = '0'">
      <table class="navigation" width="100%"
             summary="Navigation footer" cellpadding="2" cellspacing="0">
        <tr valign="middle">
          <td align="left">
            <xsl:if test="count($prev) > 0">
              <a accesskey="p">
                <xsl:attribute name="href">
                  <xsl:call-template name="href.target">
                    <xsl:with-param name="object" select="$prev"/>
                  </xsl:call-template>
                </xsl:attribute>
                <b>
                  <xsl:text>&lt;&lt;&#160;</xsl:text>
                  <xsl:apply-templates select="$prev"
                                       mode="object.title.markup"/>
                </b>
              </a>
            </xsl:if>
          </td>
          <td align="right">
            <xsl:if test="count($next) > 0">
              <a accesskey="n">
                <xsl:attribute name="href">
                  <xsl:call-template name="href.target">
                    <xsl:with-param name="object" select="$next"/>
                  </xsl:call-template>
                </xsl:attribute>
                <b>
                  <xsl:apply-templates select="$next"
                                       mode="object.title.markup"/>
                  <xsl:text>&#160;&gt;&gt;</xsl:text>
                </b>
              </a>
            </xsl:if>
          </td>
        </tr>
      </table>
    </xsl:if>
  </xsl:template>

  <!-- avoid creating multiple identical indices 
       if the stylesheets don't support filtered indices
    -->
  <xsl:template match="index"> 
    <xsl:variable name="has-filtered-index">
      <xsl:call-template name="version-greater-or-equal">
        <xsl:with-param name="ver1" select="$VERSION" />
        <xsl:with-param name="ver2">1.62</xsl:with-param>
      </xsl:call-template>
    </xsl:variable>
    <xsl:if test="($has-filtered-index = 1) or (count(@role) = 0)">
      <xsl:apply-imports/>
    </xsl:if> 
  </xsl:template>

  <xsl:template match="index" mode="toc">
    <xsl:variable name="has-filtered-index">
      <xsl:call-template name="version-greater-or-equal">
        <xsl:with-param name="ver1" select="$VERSION" />
        <xsl:with-param name="ver2">1.62</xsl:with-param>
      </xsl:call-template>
    </xsl:variable>
    <xsl:if test="($has-filtered-index = 1) or (count(@role) = 0)">
      <xsl:apply-imports/>
    </xsl:if> 
  </xsl:template>
 
</xsl:stylesheet>
